import os
import duckdb
import json
from collections import defaultdict

class NavDuckDBMaterializer:
    def __init__(self):
        # Use absolute or consistent relative paths to avoid "Ghost DB" files
        self.db_path = os.path.join("bin", "nav_domain.db")
        self.mapping_path = os.path.join("src/bin", "mapping.json")
        self.log_file = os.path.join("bin", "schema_mismatch.log")

        # Ensure the bin directory exists
        os.makedirs("bin", exist_ok=True)

        print(f"📍 ARCHITECT: Connecting to {self.db_path}")
        self.conn = duckdb.connect(self.db_path)

        # --- LOAD MAPPING ---
        with open(self.mapping_path, "r") as f:
            self.mapping = json.load(f)

        # --- ENSURE TABLES EXIST ---
        print("🏗️  Initializing Schema...")
        for msg_type, categories in self.mapping.items():
            for category, field_map in categories.items():
                table_name = category
                # inode is our PRIMARY KEY for idempotency (prevents duplicates)
                columns = ["inode BIGINT PRIMARY KEY", "timestamp_us BIGINT"]
                for target_col in field_map.values():
                    columns.append(f"{target_col} DOUBLE")

                col_defs = ", ".join(columns)
                sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({col_defs})"
                self.conn.execute(sql)

        # 🔒 LOCK THE SCHEMA: Ensures tables are visible to CLI immediately
        self.conn.commit()

        # --- META LEDGER SETUP ---
        self.conn.execute("CREATE TABLE IF NOT EXISTS meta_ledger (last_inode BIGINT)")
        res = self.conn.execute("SELECT COUNT(*) FROM meta_ledger").fetchone()[0]
        if res == 0:
            self.conn.execute("INSERT INTO meta_ledger VALUES (0)")
            self.conn.commit()

        print(f"✅ Schema finalized. Tables ready in {self.db_path}")

        # --- STATE ---
        self.batch = []
        self.batch_limit = 100  # Flush every 100 packets
        self.table_cache = {}

    def ingest(self, packet):
        """Standard entry point for incoming MAVLink packets."""
        self._commit_to_silver(packet)

        if len(self.batch) >= self.batch_limit:
            self._flush_batch()

    def _get_table_columns(self, table_name):
        """Returns ordered list of columns for a table from cache or DB."""
        if table_name not in self.table_cache:
            res = self.conn.execute(f"PRAGMA table_info('{table_name}')").fetchall()
            self.table_cache[table_name] = [col[1] for col in res]
        return self.table_cache[table_name]

    def _commit_to_silver(self, packet):
        inode = packet['inode']
        msg_type = packet['msg_type']
        raw_data = packet.get('data', {})

        # ⏱️ Robust Timestamp: Handles MAVLink's varied time sources
        ts_raw = packet.get("timestamp")
        if ts_raw is not None and ts_raw != 0:
            timestamp_us = int(ts_raw * 1_000_000)
        elif raw_data.get("time_usec") is not None:
            timestamp_us = raw_data.get("time_usec")
        else:
            timestamp_us = int(raw_data.get("time_boot_ms", 0) * 1000)

        if msg_type not in self.mapping:
            return

        # Prepare a row for every table mapped to this MAVLink message type
        for table, field_map in self.mapping[msg_type].items():
            db_cols = self._get_table_columns(table)
            if not db_cols:
                continue

            row_values = []
            has_telemetry = False

            # Drive the value extraction by the DATABASE column order
            for col in db_cols:
                if col == 'inode':
                    row_values.append(inode)
                elif col == 'timestamp_us':
                    row_values.append(timestamp_us)
                else:
                    # Find which MAVLink key maps to this DB column
                    source_key = next((k for k, v in field_map.items() if v == col), None)
                    val = raw_data.get(source_key) if source_key else None

                    if isinstance(val, list) and len(val) > 0:
                        val = val[0]

                    if val is not None:
                        has_telemetry = True
                    row_values.append(val)

            # Only batch the row if it contains actual data beyond IDs/Timestamps
            if has_telemetry:
                # Store table and column signature to ensure correct batch grouping
                self.batch.append((table, tuple(db_cols), tuple(row_values)))

    def _flush_batch(self):
        if not self.batch:
            return

        # Group by (table, col_signature) for vectorized executemany speed
        table_groups = defaultdict(list)
        max_inode_in_batch = 0

        for table, cols, vals in self.batch:
            table_groups[(table, cols)].append(vals)
            if vals[0] > max_inode_in_batch:
                max_inode_in_batch = vals[0]

        try:
            self.conn.execute("BEGIN TRANSACTION")

            for (table, cols), rows in table_groups.items():
                placeholders = ", ".join(["?"] * len(cols))
                col_names = ", ".join(cols)
                sql = f"INSERT OR REPLACE INTO {table} ({col_names}) VALUES ({placeholders})"

                # High-speed vectorized insert 🦆⚡
                self.conn.executemany(sql, rows)

            self.conn.execute("UPDATE meta_ledger SET last_inode = ?", (max_inode_in_batch,))
            self.conn.execute("COMMIT")
            print(f"💾 Flush: {len(self.batch)} packets -> {len(table_groups)} tables. Ledger: {max_inode_in_batch}")

        except Exception as e:
            if self.conn:
                self.conn.execute("ROLLBACK")
            print(f"⚠️ Flush Error: {e}")
        finally:
            self.batch.clear()

    def close(self):
        """Graceful shutdown ensures no data is left in the memory buffer."""
        print("👤 ARCHITECT: Shutting down. Flushing final batch...")
        self._flush_batch()
        if self.conn:
            self.conn.close()
            print("🔒 Vault secured.")
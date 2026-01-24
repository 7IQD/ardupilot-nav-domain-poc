import os
import duckdb
import json

class NavDuckDBMaterializer:
    def __init__(self):
        # --- Paths ---
        self.db_path = os.path.join("src/bin", "nav_domain.db")
        self.mapping_path = os.path.join("src/bin", "mapping.json")

        print("📍 DB path:", self.db_path)
        print("📍 Mapping path:", self.mapping_path)

        # --- Connect to DuckDB ---
        self.conn = duckdb.connect(self.db_path)

        # --- Load Mapping ---
        if not os.path.exists(self.mapping_path):
            raise FileNotFoundError(f"Mapping file not found: {self.mapping_path}")
        with open(self.mapping_path, "r") as f:
            mapping = json.load(f)
        self.mapping = mapping

        # --- Ensure tables exist ---
        for msg_type, categories in mapping.items():
            for table_name, field_map in categories.items():  # <-- use category as table_name
                columns = ["inode BIGINT", "timestamp_us BIGINT"]
                for target_col in field_map.values():
                    columns.append(f"{target_col} DOUBLE")
                col_defs = ", ".join(columns)
                sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({col_defs})"
                self.conn.execute(sql)
                print(f"✅ Table '{table_name}' ensured with columns: {columns}")

            col_defs = ", ".join(columns)
            sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({col_defs})"
            self.conn.execute(sql)
            print(f"✅ Table '{table_name}' ensured with columns: {columns}")

        # --- Meta Ledger ---
        self._setup_meta_ledger()

        # --- State ---
        self.next_expected = 1
        self.buffer = {}
        self.buffer_limit = 500
        self.is_quarantined = False
        self.table_cache = {}
        self.log_file = os.path.join("src/bin", "schema_mismatch.log")

    def _setup_meta_ledger(self):
        try:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS meta_ledger (
                    last_inode BIGINT
                )
            """)
            count = self.conn.execute("SELECT COUNT(*) FROM meta_ledger").fetchone()[0]
            if count == 0:
                self.conn.execute("INSERT INTO meta_ledger VALUES (0)")
                self.conn.commit()
                print("📝 meta_ledger created with last_inode=0")
            else:
                last = self.conn.execute("SELECT last_inode FROM meta_ledger").fetchone()[0]
                print(f"📝 meta_ledger exists, resuming from last_inode={last}")
        except Exception as e:
            print(f"❌ ERROR initializing meta_ledger: {e}")

    def ingest(self, packet):
        inode = packet['inode']
        msg_type = packet['msg_type']
        print(f"⬅️ ARCHITECT ← QUEUE | inode={inode} | {msg_type}")

        self._commit_to_silver(packet)

        # --- Update Meta Ledger ---
        try:
            self.conn.execute("UPDATE meta_ledger SET last_inode = ?", (inode,))
            self.conn.commit()
            print(f"💾 meta_ledger updated: last_inode={inode}")
        except Exception as e:
            print(f"⚠️ ERROR updating meta_ledger for inode {inode}: {e}")

    def _get_table_columns(self, table_name):
        if table_name in self.table_cache:
            return self.table_cache[table_name]
        try:
            res = self.conn.execute(f"PRAGMA table_info('{table_name}')").fetchall()
            cols = [col[1] for col in res]
            self.table_cache[table_name] = cols
            return cols
        except Exception:
            return []

    def _commit_to_silver(self, packet):
        msg_type = packet['msg_type']
        current_inode = packet['inode']
        raw_data = packet.get('data', {})

        # Timestamp extraction
        timestamp = (
            packet.get('timestamp_us') or
            raw_data.get('time_usec') or
            (raw_data.get('time_boot_ms', 0) * 1000)
        )

        self.next_expected = current_inode + 1

        if msg_type in self.mapping:
            try:
                self.conn.execute("BEGIN TRANSACTION")

                for table, field_map in self.mapping[msg_type].items():
                    db_cols = self._get_table_columns(table)
                    if not db_cols:
                        self._log_discrepancy(current_inode, table, "Table missing.")
                        continue

                    columns = ["inode"]
                    values = [current_inode]

                    if "timestamp_us" in db_cols:
                        columns.append("timestamp_us")
                        values.append(timestamp)

                    for source_key, target_col in field_map.items():
                        if target_col in db_cols:
                            val = raw_data.get(source_key)
                            if isinstance(val, list) and len(val) > 0:
                                val = val[0]
                            columns.append(target_col)
                            values.append(val)

                    if len(columns) > 1:
                        placeholders = ", ".join(["?"] * len(values))
                        col_names = ", ".join(columns)
                        sql = f"INSERT OR REPLACE INTO {table} ({col_names}) VALUES ({placeholders})"
                        self.conn.execute(sql, values)

                self.conn.execute("UPDATE meta_ledger SET last_inode = ?", (current_inode,))
                self.conn.execute("COMMIT")
            except Exception as e:
                if self.conn:
                    self.conn.execute("ROLLBACK")
                print(f"⚠️ Materialization Error | Inode {current_inode} [{msg_type}]: {e}")

    def _log_discrepancy(self, inode, table, message):
        with open(self.log_file, "a") as f:
            f.write(f"INODE: {inode} | TABLE: {table} | {message}\n")

    def close(self):
        if self.conn:
            self.conn.close()
            print("👤 ARCHITECT: Vault secured and closed.")

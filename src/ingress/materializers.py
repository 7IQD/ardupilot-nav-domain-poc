import duckdb
import json
import os

class NavDuckDBMaterializer:
    def __init__(self, db_path="bin/nav_domain.db", mapping_path="bin/mapping.json"):
        # Adjust paths to ensure they work from the project root or src directory
        self.db_path = db_path
        self.mapping_path = mapping_path
        self.conn = duckdb.connect(self.db_path)

        # Load the mapping policy
        with open(self.mapping_path, 'r') as f:
            self.mapping = json.load(f)

        self.next_expected = 1
        self.buffer = {}
        self.buffer_limit = 500
        self.is_quarantined = False

        # Cache table columns to avoid constant PRAGMA overhead
        self.table_cache = {}

        # Ensure log directory exists
        os.makedirs("bin", exist_ok=True)
        self.log_file = "bin/schema_mismatch.log"

        # Clear old logs on startup
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

    def ingest(self, packet):
        """High-level ingestion logic with sequence protection"""
        if self.is_quarantined:
            return

        inode = packet['inode']

        # 1. Handle Out-of-Order Packets (Buffering)
        if inode > self.next_expected:
            self.buffer[inode] = packet
            if len(self.buffer) > self.buffer_limit:
                print(f"🛑 DEADMAN TRIGGERED: Buffer Overflow at Inode {inode}")
                self.is_quarantined = True
            return

        # 2. Handle Expected Packet
        if inode == self.next_expected:
            self._commit_to_silver(packet)

            # 3. Drain Buffer for consecutive packets
            while self.next_expected in self.buffer:
                next_pkt = self.buffer.pop(self.next_expected)
                self._commit_to_silver(next_pkt)

    def _get_table_columns(self, table_name):
        """Helper to fetch actual columns from the database (with caching)"""
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
        """Audited write to DuckDB with Timestamp Sync and Idempotency"""
        msg_type = packet['msg_type']
        current_inode = packet['inode']
        raw_data = packet.get('data', {})

        # --- CRITICAL: TIMESTAMP EXTRACTION ---
        # ArduPilot uses different keys for time. We consolidate them to microseconds (us).
        timestamp = (
            packet.get('timestamp_us') or
            raw_data.get('time_usec') or
            (raw_data.get('time_boot_ms', 0) * 1000)
        )

        # Advance sequence to prevent pipeline stall
        self.next_expected = current_inode + 1

        if msg_type in self.mapping:
            try:
                self.conn.execute("BEGIN TRANSACTION")

                for table, field_map in self.mapping[msg_type].items():
                    db_cols = self._get_table_columns(table)

                    if not db_cols:
                        self._log_discrepancy(current_inode, table, "Table missing.")
                        continue

                    # Base columns
                    columns = ["inode"]
                    values = [current_inode]

                    # Auto-sync timestamp if table supports it
                    if "timestamp_us" in db_cols:
                        columns.append("timestamp_us")
                        values.append(timestamp)

                    for source_key, target_col in field_map.items():
                        if target_col in db_cols:
                            val = raw_data.get(source_key)
                            # Handle MAVLink list quirk
                            if isinstance(val, list) and len(val) > 0:
                                val = val[0]
                            columns.append(target_col)
                            values.append(val)

                    # --- THE FIX: INSERT OR REPLACE ---
                    # Handles fan-out from EKF_STATUS_REPORT or duplicate packets
                    if len(columns) > 1:
                        placeholders = ", ".join(["?"] * len(values))
                        col_names = ", ".join(columns)
                        sql = f"INSERT OR REPLACE INTO {table} ({col_names}) VALUES ({placeholders})"
                        self.conn.execute(sql, values)

                # Update the metadata ledger and commit
                self.conn.execute("UPDATE meta_ledger SET last_inode = ?", (current_inode,))
                self.conn.execute("COMMIT")

            except Exception as e:
                if self.conn:
                    self.conn.execute("ROLLBACK")
                print(f"⚠️  Materialization Error | Inode {current_inode} [{msg_type}]: {e}")

    def _log_discrepancy(self, inode, table, message):
        with open(self.log_file, "a") as f:
            f.write(f"INODE: {inode} | TABLE: {table} | {message}\n")

    def close(self):
        if self.conn:
            self.conn.close()
            print("👤 ARCHITECT: Vault secured and closed.")
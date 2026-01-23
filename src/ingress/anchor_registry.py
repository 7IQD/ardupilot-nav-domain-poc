import duckdb

class AnchorRegistry:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_table()

    def _init_table(self):
        with duckdb.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_telemetry_anchor (
                    inode INTEGER PRIMARY KEY,
                    wall_ns BIGINT,
                    boot_ms INTEGER,
                    epoch_usec BIGINT
                )
            """)

    def record_anchor(self, inode, wall_ns, boot_ms=0, epoch_usec=0):
        """Atomic write of the timing triad for a specific inode."""
        with duckdb.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO session_telemetry_anchor VALUES (?, ?, ?, ?)
            """, (inode, wall_ns, boot_ms, epoch_usec))
        return True
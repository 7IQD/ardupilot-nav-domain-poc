import duckdb
import logging

logging.basicConfig(
    filename='logs/anchor_registry.log',
    level=logging.INFO,
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("anchor_registry")

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
        logger.info(f"Anchor table initialized at {self.db_path}")

    def record_anchor(self, inode, wall_ns, boot_ms=0, epoch_usec=0):
        try:
            with duckdb.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO session_telemetry_anchor VALUES (?, ?, ?, ?)
                """, (inode, wall_ns, boot_ms, epoch_usec))
            logger.info(f"Anchor recorded: inode={inode}, wall_ns={wall_ns}")
            return True
        except Exception as e:
            logger.error(f"Failed to record anchor for inode={inode}: {e}")
            return False

import os
import time
import logging
from .anchor_registry import AnchorRegistry

logger = logging.getLogger("data_manager")

class data_manager:
    def __init__(self, log_dir, db_path):
        self.log_dir = log_dir
        self.bin_path = os.path.join(log_dir, "bronze_ledger.bin")

        # Create directories if needed
        db_folder = os.path.dirname(db_path)
        if db_folder:
            os.makedirs(db_folder, exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)

        # Anchor Registry for Silver timing
        self.anchor_reg = AnchorRegistry(db_path)

        # Initialize inode (1 KB per record)
        if os.path.exists(self.bin_path):
            self.current_inode = (os.path.getsize(self.bin_path) // 1024) + 1
        else:
            self.current_inode = 1

        logger.info(f"[INIT] DataManager initialized. Starting inode: {self.current_inode}")

    def write_bronze_with_anchor(self, raw_bytes, wall_ns, boot_ms=0, epoch_usec=0):
        """
        Atomic write: Bronze Ledger + Silver Anchor.
        Returns: (inode, wall_ns)
        """
        inode = self.current_inode

        try:
            # 1. Persist raw bytes to Bronze Ledger
            with open(self.bin_path, "ab") as f:
                f.write(raw_bytes.ljust(1024, b'\x00'))

            # 2. Record anchor in Silver (temporal alignment)
            self.anchor_reg.record_anchor(inode, wall_ns, boot_ms, epoch_usec)

            logger.info(f"[ATOMIC] Inode {inode} -> Bronze Saved & Anchored at {wall_ns} ns")
            self.current_inode += 1
            return inode, wall_ns

        except Exception as e:
            logger.error(f"[ERROR] Failed to write inode {inode}: {e}")
            raise

import os
import time
from .anchor_registry import AnchorRegistry

class DataManager:
    def __init__(self, log_dir, db_path):
        self.log_dir = log_dir
        # We use bin_path consistently here
        self.bin_path = os.path.join(log_dir, "bronze_ledger.bin")

        # Create DB folder if it doesn't exist
        db_folder = os.path.dirname(db_path)
        if db_folder:
            os.makedirs(db_folder, exist_ok=True)

        os.makedirs(log_dir, exist_ok=True)

        self.anchor_reg = AnchorRegistry(db_path)

        # Initialize inode (simplified 1KB logic to match your seek plan)
        if os.path.exists(self.bin_path):
            self.current_inode = (os.path.getsize(self.bin_path) // 1024) + 1
        else:
            self.current_inode = 1

    def write_bronze_with_anchor(self, raw_bytes, wall_ns, boot_ms=0, epoch_usec=0):
        """
        ATOMIC LOCK: Writes raw bytes to Bronze and metadata to Anchor.
        Returns: (inode, wall_ns)
        """
        # 1. Assign Inode
        inode = self.current_inode

        # 2. Persistence (Q1: Bronze)
        # Using self.bin_path to match the __init__
        with open(self.bin_path, "ab") as f:
            # Padded to 1024 to keep your inode math (size // 1024) consistent
            f.write(raw_bytes.ljust(1024, b'\x00'))

        # 3. Anchoring (Silver Timing)
        self.anchor_reg.record_anchor(inode, wall_ns, boot_ms, epoch_usec)

        # 4. Print Validation Hook
        print(f"[CONTRACT-ATOMIC] Inode {inode} -> Bronze Saved & Anchored at {wall_ns}ns")

        self.current_inode += 1
        return inode, wall_ns
import os
import shutil
import logging

logger = logging.getLogger("SYS_CLERK")

class SysClerk:
    def __init__(self, mission_id):
        self.mission_id = mission_id
        self.source_dir = "bin/vault/vault_b"
        # Mission-scoped warehouse path
        self.target_dir = f"bin/vault/vault_c/{self.mission_id}/sys_warehouse"

        os.makedirs(self.target_dir, exist_ok=True)
        logger.info(f"✅ SysClerk initialized for {self.target_dir}")

    def process_vault_b(self):
        """Moves SYS segments from Vault B to the Mission Warehouse."""
        if not os.path.exists(self.source_dir):
            return

        for filename in os.listdir(self.source_dir):
            if filename.startswith("sys_") and filename.endswith(".parquet"):
                src_path = os.path.join(self.source_dir, filename)
                dst_path = os.path.join(self.target_dir, filename)

                try:
                    shutil.move(src_path, dst_path)
                except Exception as e:
                    logger.error(f"❌ Failed to move {filename}: {e}")
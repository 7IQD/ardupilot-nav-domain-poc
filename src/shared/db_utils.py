import os
import shutil

class DatabaseManager:
    def __init__(self, warehouse_path: str = "bin/vault/warehouse/"):
        self.warehouse_path = warehouse_path

    def initialize_warehouse(self, overwrite: bool = True):
        """
        Clears existing data in the warehouse to allow for fresh testing
        without stale telemetry interference.
        """
        if overwrite and os.path.exists(self.warehouse_path):
            print(f"DB_UTILS: Overwriting warehouse at {self.warehouse_path}")
            for filename in os.listdir(self.warehouse_path):
                file_path = os.path.join(self.warehouse_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Error during warehouse reset: {e}")

        os.makedirs(self.warehouse_path, exist_ok=True)
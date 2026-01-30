import os
import pandas as pd

class DatabaseManager:
    """
    ROLE: The Clerk.
    CONCEPT: Ensure the physical vault is ready for deposits.
    """
    def __init__(self):
        self.vault_base = "bin/vault"
        self.folders = [
            "warehouse",
            "gold/nav_pilot",
            "gold/nav_ekf",
            "gold/nav_forensics",
            "dashboard/nav_pilot",
            "dashboard/nav_ekf"
        ]

    def ensure_vault_structure(self):
        """Creates the directory tree if it doesn't exist."""
        for folder in self.folders:
            path = os.path.join(self.vault_base, folder)
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                print(f"📁 Created Vault: {path}")

    def initialize_warehouse(self, overwrite=False):
        """Ensures nav_master.parquet exists in the Silver layer."""
        path = "bin/vault/warehouse/nav_master.parquet"
        if overwrite and os.path.exists(path):
            os.remove(path)
            print("🧹 Overwriting Database for fresh test run.")

        if not os.path.exists(path):
            # Create an empty template with the expected Silver columns
            df = pd.DataFrame(columns=['best_ts', 'mavpackettype', 'lat', 'lon', 'alt', 'relative_alt'])
            df.to_parquet(path, index=False)
            print(f"✨ Initialized Silver Warehouse: {path}")
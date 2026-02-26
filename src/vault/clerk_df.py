import os
import shutil


class ClerkDF:
    def __init__(self):
        # Resolve project root
        self.root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../")
        )

        # Staging (Parquet shards)
        self.vault_b = os.path.join(self.root, "bin/vault/vault_b")

        # Final masters (Gold layer)
        self.warehouse_df = os.path.join(self.root, "bin/vault/warehouse_df")

        os.makedirs(self.vault_b, exist_ok=True)
        os.makedirs(self.warehouse_df, exist_ok=True)

    # -----------------------------
    # STAGING CONTROL
    # -----------------------------
    def reset_staging(self):
        """
        Surgically clears Vault B to prevent cross-mission shard contamination.
        Warehouse remains untouched.
        """
        if not os.path.exists(self.vault_b):
            return

        for name in os.listdir(self.vault_b):
            path = os.path.join(self.vault_b, name)
            try:
                if os.path.isfile(path) or os.path.islink(path):
                    os.unlink(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
            except Exception as e:
                print(f"⚠️ [Clerk-DF] Failed to delete {path}: {e}")

        print("✅ [Clerk-DF] Vault_B (Staging) reset complete.")

    # -----------------------------
    # WAREHOUSE CONTROL (Manual)
    # -----------------------------
    def clear_warehouse(self):
        """
        Hard reset of finalized master Parquets.
        Use only for full system refresh.
        """
        if not os.path.exists(self.warehouse_df):
            return

        for name in os.listdir(self.warehouse_df):
            path = os.path.join(self.warehouse_df, name)
            if os.path.isfile(path):
                os.unlink(path)

        print("🚨 [Clerk-DF] Warehouse masters cleared.")

    # -----------------------------
    # PATH RESOLUTION
    # -----------------------------
    def get_warehouse_path(self, domain_name):
        """
        Deterministic gold master path resolver.
        Used by df_refinery to write canonical domain masters.
        """
        return os.path.join(
            self.warehouse_df,
            f"{domain_name.lower()}_df_master.parquet"
        )
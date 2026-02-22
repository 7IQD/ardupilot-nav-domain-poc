import os
import shutil

class ClerkDF:
    def __init__(self):
        # Resolve paths relative to the project root
        self.root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        self.vault_b = os.path.join(self.root, "bin/vault/vault_b")
        self.warehouse_df = os.path.join(self.root, "bin/vault/warehouse_df")

        # Ensure directories exist
        os.makedirs(self.vault_b, exist_ok=True)
        os.makedirs(self.warehouse_df, exist_ok=True)

    def reset(self):
        """
        SURGICAL RESET: Only clears the staging shards (Vault B).
        Used by the refinery to clean up after a successful mission injection.
        """
        if os.path.exists(self.vault_b):
            for filename in os.listdir(self.vault_b):
                file_path = os.path.join(self.vault_b, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"⚠️ [Clerk] Failed to delete {file_path}: {e}")
        print("✅ [Clerk] Staging area (Vault B) reset. Warehouse remains intact.")

    def clear_warehouse(self):
        """
        HARD RESET: Wipes the finalized masters (Warehouse).
        Call this manually or from df_main if you want a totally fresh start.
        """
        if os.path.exists(self.warehouse_df):
            for filename in os.listdir(self.warehouse_df):
                file_path = os.path.join(self.warehouse_df, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
        print("🚨 [Clerk] Warehouse masters wiped.")

    def finalize_run(self, domains=None):
        """
        LEGACY/FALLBACK: Performs a raw merge without Mission ID.
        In your new architecture, df_refinery.py replaces the need for this.
        """
        print("📦 [Clerk] Warning: finalize_run() called. This skips Mission ID refinement.")
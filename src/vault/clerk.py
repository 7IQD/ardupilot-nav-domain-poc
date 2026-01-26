import os
import shutil
import pandas as pd
import glob

class Clerk:
    def __init__(self):
        self.vault_b = 'bin/vault/vault_b'
        self.warehouse = 'bin/vault/warehouse'
        os.makedirs(self.warehouse, exist_ok=True)

    def reset_vault(self):
        """Fulfills Overwrite requirement [2026-01-15]"""
        if os.path.exists(self.vault_b):
            shutil.rmtree(self.vault_b)
        os.makedirs(self.vault_b, exist_ok=True)
        print("🧹 [CLERK] Vault B wiped. System ready for fresh run.")

    def finalize_run(self):
        """Fulfills Complete File requirement [2026-01-26]"""
        for domain in ['nav', 'sys']:
            search_pattern = os.path.join(self.vault_b, f"{domain}_raw_*.parquet")
            files = sorted(glob.glob(search_pattern))

            if not files:
                continue

            print(f"📦 [CLERK] Consolidating {domain.upper()} segments...")
            df_list = [pd.read_parquet(f) for f in files]
            master_df = pd.concat(df_list, ignore_index=True)

            output_path = os.path.join(self.warehouse, f"{domain}_master.parquet")
            master_df.to_parquet(output_path)
            print(f"✅ [CLERK] Created: {output_path}")
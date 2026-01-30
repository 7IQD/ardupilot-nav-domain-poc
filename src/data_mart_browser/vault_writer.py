import os
import pandas as pd
from datetime import datetime

class VaultWriter:
    """
    ROLE: The Clerk for Evidence.
    CONCEPT: Freeze human-validated insights into immutable artifacts.
    """
    def __init__(self, mission_id, product_type):
        self.vault_dir = f"bin/vault/dashboard/nav_{product_type}/{mission_id}/"
        os.makedirs(self.vault_dir, exist_ok=True)

    def capture(self, fig, df_slice, note="Manual Insight"):
        """
        Freezes the current visual state and the underlying data.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 1. Save Visual Proof (PNG)
        fig.savefig(f"{self.vault_dir}snapshot_{timestamp}.png")

        # 2. Save Data Proof (CSV Slice for forensic portability)
        df_slice.to_csv(f"{self.vault_dir}data_{timestamp}.csv", index=False)

        # 3. Create Audit Trail (Markdown)
        with open(f"{self.vault_dir}notes.md", "a") as f:
            f.write(f"\n## {timestamp}\n- **Analyst Note:** {note}\n- **Data Rows:** {len(df_slice)}\n")

        print(f"✅ Evidence Locked in Vault: {self.vault_dir}")
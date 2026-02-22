import os
import pandas as pd
from datetime import datetime

class VaultWriter:
    """
    ROLE: The Clerk for Evidence.
    CONCEPT: Freeze human-validated insights into immutable artifacts.
    """
    def __init__(self, mission_id, product_type):
        # --- ROBUST PATH LOGIC ---
        # Locates project root relative to this file's position in src/dashboard/
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.abspath(os.path.join(self.script_dir, "../../"))

        # Define the target vault directory
        self.vault_dir = os.path.join(
            self.project_root,
            "bin/vault/dashboard",
            f"nav_{product_type}",
            mission_id
        )

        # Ensure the directory exists
        os.makedirs(self.vault_dir, exist_ok=True)

    def capture(self, fig, df_slice, note="Manual Insight"):
        """
        Freezes the current visual state and the underlying data.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 1. Save Visual Proof (PNG)
        img_path = os.path.join(self.vault_dir, f"snapshot_{timestamp}.png")
        fig.savefig(img_path)

        # 2. Save Data Proof (CSV Slice for forensic portability)
        csv_path = os.path.join(self.vault_dir, f"data_{timestamp}.csv")
        df_slice.to_csv(csv_path, index=False)

        # 3. Create Audit Trail (Markdown)
        md_path = os.path.join(self.vault_dir, "notes.md")
        with open(md_path, "a") as f:
            f.write(f"\n## {timestamp}\n")
            f.write(f"- **Analyst Note:** {note}\n")
            f.write(f"- **Data Rows:** {len(df_slice)}\n")
            f.write(f"- **Image Ref:** snapshot_{timestamp}.png\n")

        print(f"✅ Evidence Locked in Vault: {self.vault_dir}")
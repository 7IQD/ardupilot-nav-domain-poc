#!/usr/bin/env python3
import os, sys, time

# --- DYNAMIC PATH INJECTION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# --- IMPORTS ---
from src.vault.clerk_df import ClerkDF
from src.weaving.ingest_df.nav_df_architect import NavDFArchitect
from src.weaving.ingest_df.est_df_architect import EstDFArchitect
from src.weaving.ingest_df.com_df_architect import ComDFArchitect
from src.weaving.ingest_df.sys_df_architect import SysDFArchitect
from src.weaving.ingest_df.power_df_architect import PowerDFArchitect

# --- DOMAIN MAP ---
DOMAINS = {
    "nav": NavDFArchitect,
    "est": EstDFArchitect,
    "com": ComDFArchitect,
    "sys": SysDFArchitect,
    "power": PowerDFArchitect
}

def main():
    total_start = time.time()
    BIN_SOURCE = os.path.join(ROOT, "bin/vault/df_source")
    TARGET_BIN = os.path.join(BIN_SOURCE, "clean_20260213_133342.BIN")

    print(f"🌐 Starting Multi-Domain DF Extraction | BIN: {os.path.basename(TARGET_BIN)}\n")

    # 1️⃣ RESET (Optional)
    clerk = ClerkDF()
    if input("Reset vault_b staging area? (y/n): ").strip().lower() == "y":
        clerk.reset() # This should only clear vault_b, not the warehouse

    # 2️⃣ DOMAIN PROCESSING (Architecture Phase)
    processed_domains = []
    for domain_name, architect_cls in DOMAINS.items():
        if input(f"Process {domain_name.upper()}? (y/n): ").strip().lower() == "y":
            print(f"🏁 Extracting {domain_name.upper()} to shards...")
            arch = architect_cls(TARGET_BIN)
            success = arch.process_flight()
            if success:
                processed_domains.append(domain_name)

    # 3️⃣ HANDSHAKE GAP (Crucial Change)
    print("\n✅ Extraction Phase Complete.")
    print("📢 Shards are waiting in vault_b/.")
    print("🚀 NEXT STEP: Run 'python3 bin/df_refinery.py' to inject Mission ID and consolidate.")

if __name__ == "__main__":
    main()
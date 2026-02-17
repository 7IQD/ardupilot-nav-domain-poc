#!/usr/bin/env python3
import os
import sys
import time

# --- DYNAMIC PATH INJECTION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # src/runner
ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))  # project root
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# --- IMPORTS USING SRC PACKAGE PREFIX ---
from src.vault.clerk_df import ClerkDF
from src.weaving.ingest_df.nav_df_architect import NavDFArchitect
from src.weaving.ingest_df.est_df_architect import EstDFArchitect
from src.weaving.ingest_df.com_df_architect import ComDFArchitect
from src.weaving.ingest_df.sys_df_architect import SysDFArchitect
from src.weaving.ingest_df.power_df_architect import PowerDFArchitect

# --- BIN SOURCE ---
BIN_SOURCE = os.path.join(ROOT, "bin/vault/df_source")
TARGET_BIN = os.path.join(BIN_SOURCE, "clean_20260213_133342.BIN")

# --- DOMAIN MAP ---
DOMAINS = {
    "nav": NavDFArchitect,
    "est": EstDFArchitect,
    "com": ComDFArchitect,
    "sys": SysDFArchitect,
    "power": PowerDFArchitect
}

def user_confirm(domain_name):
    """Ask user whether to process a domain"""
    while True:
        resp = input(f"Process {domain_name.upper()} domain? (y/n): ").strip().lower()
        if resp in ("y", "n"):
            return resp == "y"

def process_domain(domain_name, architect_cls):
    print(f"\n🏁 Starting {domain_name.upper()} domain processing...")
    if not os.path.exists(TARGET_BIN):
        print(f"❌ BIN file missing: {TARGET_BIN}")
        return False
    arch = architect_cls(TARGET_BIN)
    return arch.process_flight()

def main():
    total_start = time.time()
    print(f"🌐 Starting Multi-Domain DF Pipeline | Mission: {os.path.basename(TARGET_BIN)}\n")

    # 1️⃣ RESET
    clerk = ClerkDF()
    if user_confirm("reset vault & warehouse"):
        clerk.reset()

    # 2️⃣ DOMAIN PROCESSING LOOP
    processed_domains = []
    for domain_name, architect_cls in DOMAINS.items():
        if user_confirm(domain_name):
            success = process_domain(domain_name, architect_cls)
            if success:
                processed_domains.append(domain_name)
        else:
            print(f"⏭️  Skipping {domain_name.upper()} domain...")

    # 3️⃣ CONSOLIDATION
    if processed_domains:
        print("\n📦 Consolidating domains into warehouse_df...")
        clerk.finalize_run(domains=processed_domains)
    else:
        print("⚠️  No domains processed; skipping consolidation.")

    print(f"\n🏁 Pipeline Complete | Total Time: {time.time() - total_start:.2f}s", flush=True)
    print(f"✅ Warehouse Masters are located in: {clerk.warehouse_df}", flush=True)
    print("\n✅ df_main.py has finished generating master parquets.", flush=True)
    print("📢 Next action: Create DuckDB views using create_views.py", flush=True)

if __name__ == "__main__":
    main()

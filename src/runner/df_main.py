#!/usr/bin/env python3
import os
import sys
import time

# --- DYNAMIC PATH INJECTION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../"))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))

if SRC_ROOT not in sys.path: sys.path.insert(0, SRC_ROOT)
if PROJECT_ROOT not in sys.path: sys.path.insert(0, PROJECT_ROOT)

from vault.clerk_df import ClerkDF
from weaving.ingest_df.nav_df_architect import NavDFArchitect

# Paths
BIN_SOURCE = os.path.join(PROJECT_ROOT, "bin/vault/df_source")
TARGET_BIN = os.path.join(BIN_SOURCE, "clean_20260213_133342.BIN")

def main():
    total_start = time.time()
    # ENHANCEMENT: Multi-domain support list
    DOMAINS = ["nav"]

    print(f"🏁 Starting DF Waterfall Pipeline | Mission: {os.path.basename(TARGET_BIN)}")

    # 1️⃣ [PASS 1] PURGE
    clerk = ClerkDF()
    clerk.reset()

    # 2️⃣ [PASS 2] EXTRACTION
    if not os.path.exists(TARGET_BIN):
        print(f"❌ Source .BIN missing: {TARGET_BIN}")
        return

    ext_start = time.time()
    # Architect processes the BIN and dumps shards into vault_b
    architect = NavDFArchitect(TARGET_BIN)
    success = architect.process_flight()

    if not success:
        print("❌ Extraction failed. Aborting.")
        return
    print(f"⏱️  Extraction Duration: {time.time() - ext_start:.2f}s")

    # 3️⃣ [PASS 3] CONSOLIDATION
    cons_start = time.time()
    # The Clerk now handles multi-domain consolidation using DuckDB
    clerk.finalize_run(domains=DOMAINS)
    print(f"⏱️  Consolidation Duration: {time.time() - cons_start:.2f}s")

    print(f"🏁 Pipeline Complete. Total Time: {time.time() - total_start:.2f}s")

if __name__ == "__main__":
    main()
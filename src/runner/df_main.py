#!/usr/bin/env python3
"""
df_main.py
Primary Entry Point for DataFlash Ingress Pipeline
"""

import os
import sys
import argparse

# --- PERMANENT PATH FIX ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# --- IMPORTS ---
try:
    from weaving.ingest_df.df_action_map import DFActionMap
    from weaving.ingest_df.df_mav_ingress_architect import DFIngressMavArchitect
    from vault.clerk_df import ClerkDF
except ImportError as e:
    print(f"❌ Critical Error: Could not find project modules. {e}")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="ArduPilot DataFlash Ingress Runner")
    parser.add_argument("bin_path", help="Path to the .BIN flight log")
    args = parser.parse_args()

    # Initialize Clerk
    clerk = ClerkDF()

    print("=" * 60)
    print("🧹 Stage 1: Clearing Staging Areas...")

    # FIXED: Using the actual method name found via grep
    if hasattr(clerk, 'reset_staging'):
        clerk.reset_staging()
    else:
        # Fallback if names change again
        print("⚠️  Warning: reset_staging not found, attempting manual clear...")
        if os.path.exists(clerk.vault_b):
            import shutil
            shutil.rmtree(clerk.vault_b)
            os.makedirs(clerk.vault_b, exist_ok=True)

    print(f"🚀 Stage 2: Ingress from {os.path.basename(args.bin_path)}...")
    print("=" * 60)

    # Main Processing Loop
    for domain in DFActionMap.get_domains():
        msg_types = DFActionMap.get_msg_types(domain)

        if not msg_types:
            continue

        print(f"📡 Processing: {domain: <6} | Signals: {msg_types}")

        architect = DFIngressMavArchitect(
            bin_path=args.bin_path,
            domain_key=domain,
            msg_types=msg_types
        )

        architect.process_flight()

    print("=" * 60)
    print("✅ Stage 3: Ingress Pipeline Complete.")
    print("=" * 60)

if __name__ == "__main__":
    main()
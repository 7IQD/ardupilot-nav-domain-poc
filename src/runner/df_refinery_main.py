#!/usr/bin/env python3
"""
df_refinery_main.py
Execution wrapper for the Domain Refinery.

Purpose:
- Ensure correct PYTHONPATH resolution
- Safely import and trigger df_refinery
- Handle failures cleanly
"""

import sys
import os

# ✅ Add src/ as root so vault/ and weaving/ are importable
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../src")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ✅ Safe import (prevents silent crash)
try:
    from weaving.ingest_df.df_refinery import main as refine_main
except Exception as e:
    print(f"🚨 Import Failure: {e}")
    sys.exit(1)


def main():
    print("🚀 Starting Domain Refinery...")
    refine_main()
    print("🏁 Domain Refinery Completed.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Refinery Interrupted by User.")
        sys.exit(1)
    except Exception as e:
        print(f"🚨 Critical Failure in Refinery Execution: {e}")
        sys.exit(1)
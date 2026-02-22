#!/usr/bin/env python3
from src.core.domain_marts.mart_manager import refresh_all_marts

if __name__ == "__main__":
    print("🚀 Running DF Mart Refresh...")
    refresh_all_marts()
    print("✅ DF Marts Refresh Complete.")

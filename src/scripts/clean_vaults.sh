#!/bin/bash
# Total Mess Clearance for Ardupilot Nav Domain

echo "🧹 Purging interim artifacts and shadow databases..."

# 1. Kill the Shadow DB (Keep the root one if you wish, or kill both to be safe)
rm -f src/bin/nav_domain.db
rm -f bin/nav_domain.db

# 2. Clear out the interim vault folders (Bronze/Silver staging)
rm -rf bin/vault/vault_a/* bin/vault/vault_b/* bin/vault/vault_c/*

# 3. Clear the Dashboard Visual Cache (Targets MARATHON_01 and friends)
rm -rf bin/vault/dashboard/*

# 4. Clear the binary ledger from ingress
rm -f src/ingress/bin/bronze_ledger.bin

echo "✅ Environment Aligned. Ready for fresh Ingestion/Refinery run."
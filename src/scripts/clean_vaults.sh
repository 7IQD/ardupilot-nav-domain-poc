#!/bin/bash
# 2026 ArduPilot POC Cleanup Utility

echo "🧹 Purging all Vaults for a fresh test..."

# 1. Clear Staging Areas (A and B)
rm -f bin/vault/vault_a/*.db
rm -f bin/vault/vault_b/*.db

# 2. Clear the Warehouse (C) - As per overwrite instruction
rm -f bin/vault/vault_c/*.db

# 3. Clear the Audit Logs
rm -f logs/vault_activity.log

echo "✅ System Reset. Ready for next simulation."
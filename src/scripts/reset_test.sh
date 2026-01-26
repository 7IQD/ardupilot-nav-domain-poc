#!/bin/bash
# Resolve absolute path to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

echo "🔄 Resetting environment from: $PROJECT_ROOT"

# Clean Database Vault
rm -rf "$PROJECT_ROOT/bin/vault"/nav_seg_*.db
echo "🗑️  Vault Cleared."

# Clean Activity Logs
rm -rf "$PROJECT_ROOT/logs"/vault_activity.log*
echo "📝 Logs Wiped."

echo "✅ System ready for 2026 Flight Test."
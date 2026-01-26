#!/bin/bash

echo "--------------------------------------------------"
echo "RUNNING NAVIGATION DOMAIN PRE-FLIGHT AUDIT"
echo "--------------------------------------------------"

echo "[1/3] VERIFYING BRIDGE CONNECTIVITY..."
python3 core/verify_bridge.py || echo "⚠️ Bridge verification failed."

echo ""
echo "[2/3] FETCHING LATEST SYNCHRONIZED TELEMETRY..."
python3 core/inspect_flight.py || echo "⚠️ Telemetry inspection failed."

echo ""
echo "[3/3] CHECKING DUCKDB META LEDGER AND SILVER TABLES..."
python3 - <<END
import duckdb
import json
import os

db_path = "src/bin/nav_domain.db"
mapping_path = "src/bin/mapping.json"

if not os.path.exists(db_path):
    print(f"⚠️ DuckDB file not found: {db_path}")
    exit(1)

if not os.path.exists(mapping_path):
    print(f"⚠️ Mapping file not found: {mapping_path}")
    exit(1)

conn = duckdb.connect(db_path)

# --- META LEDGER CHECK ---
print("\n=== META LEDGER ===")
try:
    last_inode = conn.execute("SELECT last_inode FROM meta_ledger").fetchone()[0]
    print(f"Last processed inode: {last_inode}")
except Exception as e:
    print(f"⚠️ Meta ledger missing or unreadable: {e}")

# --- LOAD MAPPING TO GET TABLES ---
with open(mapping_path, "r") as f:
    mapping = json.load(f)

tables_to_check = set()
for msg_type, tbl_map in mapping.items():
    tables_to_check.update(tbl_map.keys())

# --- SILVER TABLES CHECK ---
print("\n=== SILVER TABLES CHECK ===")
for table in sorted(tables_to_check):
    try:
        cols = conn.execute(f"PRAGMA table_info('{table}')").fetchall()
        col_names = [c[1] for c in cols]
        rows = conn.execute(f"SELECT * FROM {table} LIMIT 3").fetchall()
        row_count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

        print(f"\nTable: {table}")
        print(f"Columns: {col_names}")
        print(f"Sample rows (up to 3): {rows}")
        print(f"Row count: {row_count}")

    except Exception as e:
        print(f"⚠️ Table {table} missing or unreadable: {e}")

conn.close()
END

echo ""
echo "PRE-FLIGHT AUDIT COMPLETE"
echo "--------------------------------------------------"

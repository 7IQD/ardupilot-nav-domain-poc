import duckdb
import json
import os

DB_PATH = os.path.join("..", "bin", "nav_domain.db")   # <-- relative to tests folder
MAPPING_PATH = os.path.join("..", "bin", "mapping.json")

conn = duckdb.connect(DB_PATH, read_only=True)

with open(MAPPING_PATH, 'r') as f:
    mapping = json.load(f)

print("DB and mapping loaded successfully.")
# You can now continue to fetch table columns and compare

# 3. Helper to get actual table columns
def get_table_columns(table_name):
    try:
        res = conn.execute(f"PRAGMA table_info('{table_name}')").fetchall()
        return [col[1] for col in res]
    except Exception:
        return []

# 4. Check each table from mapping
for msg_type, tables_map in mapping.items():
    for table, field_map in tables_map.items():
        db_cols = get_table_columns(table)
        mapping_cols = list(field_map.values())
        print(f"\nTable: {table}")
        print(f" DB columns     : {db_cols}")
        print(f" Mapping columns: {mapping_cols}")
        missing = [col for col in mapping_cols if col not in db_cols]
        if missing:
            print(f" ❌ Missing in DB: {missing}")
        else:
            print(f" ✅ All mapping columns exist in DB")

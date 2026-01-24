import duckdb
import os

# Resolve DB path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "../bin/nav_domain.db")

if not os.path.exists(DB_PATH):
    raise FileNotFoundError(f"DB file not found: {DB_PATH}")

print(f"📡 Scanning Vault at: {DB_PATH}")

conn = duckdb.connect(DB_PATH)

# Assuming you've already connected with 'conn'
print(conn.execute("DESCRIBE silver.nav_state").fetchdf()[['column_name', 'column_type']])
# --- Schemas ---
print("\n📂 --- Schemas Found ---")
schemas = conn.execute("SELECT schema_name FROM information_schema.schemata").fetchdf()
print(schemas)

# --- Tables in Silver ---
print("\n📊 --- Tables in Silver ---")
tables_silver = conn.execute("""
SELECT table_name
FROM information_schema.tables
WHERE table_schema='silver'
""").fetchdf()
print(tables_silver)

# --- Views in Gold ---
print("\n🥇 --- Views in Gold ---")
views_gold = conn.execute("""
SELECT table_name
FROM information_schema.views
WHERE table_schema='gold'
""").fetchdf()
print(views_gold)

# --- Columns ---
if not tables_silver.empty:
    print("\n📝 --- Columns in silver.nav_state ---")
    print(conn.execute("DESCRIBE silver.nav_state").fetchdf())

if not views_gold.empty:
    print("\n📝 --- Columns in gold.nav_context ---")
    print(conn.execute("DESCRIBE gold.nav_context").fetchdf())


conn.close()

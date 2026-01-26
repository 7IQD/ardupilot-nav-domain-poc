import duckdb

# Connect to the vault we just initialized
conn = duckdb.connect("../bin/nav_domain.db")

print("📂 --- Schemas Found ---")
# This shows 'main', 'silver', and 'gold'
print(conn.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'pg_catalog')").fetchdf())

print("\n📊 --- Tables & Views ---")
# This lists every table and view across all schemas
print(conn.execute("SELECT table_schema, table_name, table_type FROM information_schema.tables ORDER BY table_schema").fetchdf())

conn.close()
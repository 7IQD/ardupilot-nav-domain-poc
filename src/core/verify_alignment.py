import duckdb
import json

def verify_vault_alignment(db_path, mapping_path):
    conn = duckdb.connect(db_path)
    with open(mapping_path, 'r') as f:
        mapping = json.load(f)

    print(f"🔍 Auditing Alignment: {db_path} <---> {mapping_path}\n" + "-"*50)

    for msg_type, tables in mapping.items():
        for table_name, field_map in tables.items():
            # Get Actual DB Schema
            db_info = {row[1]: row[2] for row in conn.execute(f"PRAGMA table_info('{table_name}')").fetchall()}

            if not db_info:
                print(f"❌ TABLE MISSING: {table_name}")
                continue

            print(f"📊 Table: {table_name} ({msg_type})")
            for mav_field, sql_col in field_map.items():
                if sql_col in db_info:
                    print(f"  ✅ Match: {mav_field} -> {sql_col} ({db_info[sql_col]})")
                else:
                    print(f"  ⚠️  MISALIGNMENT: Field '{mav_field}' maps to '{sql_col}', but '{sql_col}' is missing in DB!")
            print("")

    conn.close()

if __name__ == "__main__":
    verify_vault_alignment("bin/nav_domain.db", "bin/mapping.json")
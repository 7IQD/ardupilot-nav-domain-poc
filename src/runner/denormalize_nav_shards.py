import duckdb
import os
import glob
import time

# 1. Paths
VAULT = "/home/ni/ardupilot-nav-domain-poc/bin/vault/vault_b"
WAREHOUSE = "/home/ni/ardupilot-nav-domain-poc/warehouse_df"
DB_PATH = os.path.join(WAREHOUSE, "nav_domain_master.db")

def build_final_nav_mart():
    if not os.path.exists(WAREHOUSE):
        os.makedirs(WAREHOUSE)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    con = duckdb.connect(DB_PATH)
    start_time = time.time()

    print(f"🚀 Scaling to 382 Shards using updated NAV_DOMAIN definitions...")

    try:
        # Step 1: Bulk Ingest with union_by_name to create the 'Full Spread'
        # This respects the FMT definitions and fills NULLs for missing fields.
        con.execute(f"""
            CREATE TABLE nav_master AS
            SELECT * FROM read_parquet('{VAULT}/nav_domain_shard_*.parquet', union_by_name=True)
            ORDER BY inode;
        """)

        # Step 2: Verification against your Promotion List
        # We check if DCM, POS, and GPA are now correctly recognized as NAV members.
        promo_list = ('ATT', 'AHR2', 'GPS', 'GPSS', 'XKF1', 'XKF2', 'XKF3', 'XKF4', 'XKF5',
                      'XKFS', 'XKQ', 'XKT', 'XKTV', 'XKV1', 'XKV2', 'ANG', 'RATE', 'CTUN',
                      'ORGN', 'PID1', 'PID2', 'PID3', 'DCM', 'POS', 'GPA', 'PIDA', 'PIDP',
                      'PIDR', 'PIDY')

        audit = con.execute(f"""
            SELECT
                msg_type,
                count(*) as tally
            FROM nav_master
            WHERE msg_type NOT IN {promo_list}
            GROUP BY msg_type
        """).fetchall()

        # Reporting
        cols = con.execute("SELECT count(*) FROM (DESCRIBE nav_master)").fetchone()[0]
        rows = con.execute("SELECT count(*) FROM nav_master").fetchone()[0]

        print("\n" + "="*50)
        print("🏁 AVIATION-GRADE NAV-MART COMPLETE")
        print("="*50)
        print(f"Total Rows:        {rows:,}")
        print(f"Full Spread Width: {cols} Columns")
        print(f"Domain Leakage:    {len(audit)} types found outside definitions")
        print(f"Total Time:        {time.time() - start_time:.2f}s")
        print("="*50)

    except Exception as e:
        print(f"❌ Ingest Failed: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    build_final_nav_mart()
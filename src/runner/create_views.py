#!/usr/bin/env python3
import os
import duckdb

# --- PATH CONFIGURATION ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
WAREHOUSE_DIR = os.path.join(PROJECT_ROOT, "bin/vault/warehouse_df")
DB_PATH = os.path.join(WAREHOUSE_DIR, "drone_df_views.db")

# Source Parquet Path
NAV_PARQUET = os.path.join(WAREHOUSE_DIR, "nav_df_master.parquet")

def main():
    print(f"🚀 Initializing Medallion Pipeline...")

    if not os.path.exists(NAV_PARQUET):
        print(f"❌ ERROR: Source master not found: {NAV_PARQUET}")
        return

    # Connect to the persistent DuckDB
    conn = duckdb.connect(DB_PATH)

    try:
        # ---------------------------------------------------------
        # 🥈 SILVER LAYER: fact_nav_events
        # Immutable Ledger of every message found in the BIN
        # ---------------------------------------------------------
        print("🥈 Deploying Silver Layer: fact_nav_events...")
        conn.execute(f"""
            CREATE OR REPLACE TABLE fact_nav_events AS
            SELECT * FROM read_parquet('{NAV_PARQUET}')
        """)

        # ---------------------------------------------------------
        # 🥇 GOLD LAYER: fact_nav_state
        # State Reconstruction via LOCF (Last Observation Carried Forward)
        # ---------------------------------------------------------
        print("🥇 Deploying Gold Layer: fact_nav_state...")
        # (TimeUS, inode) tuple ensures perfect deterministic ordering
        conn.execute("""
            CREATE OR REPLACE TABLE fact_nav_state AS
            SELECT
                *,
                LAST_VALUE(Lat IGNORE NULLS) OVER (
                    PARTITION BY mission_id ORDER BY TimeUS ASC, inode ASC
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) as aligned_lat,
                LAST_VALUE(Lng IGNORE NULLS) OVER (
                    PARTITION BY mission_id ORDER BY TimeUS ASC, inode ASC
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) as aligned_lng,
                LAST_VALUE(RelHomeAlt IGNORE NULLS) OVER (
                    PARTITION BY mission_id ORDER BY TimeUS ASC, inode ASC
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) as aligned_alt,
                LAST_VALUE(RelOriginAlt IGNORE NULLS) OVER (
                    PARTITION BY mission_id ORDER BY TimeUS ASC, inode ASC
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) as aligned_origin
            FROM fact_nav_events;
        """)

        # ---------------------------------------------------------
        # 🔭 SEMANTIC LAYER: view_nav_monitor
        # The Final UI Contract with Quoted Case-Sensitive Aliases
        # ---------------------------------------------------------
        print("🔭 Deploying Semantic Layer: view_nav_monitor...")
        conn.execute("""
            CREATE OR REPLACE VIEW view_nav_monitor AS
            SELECT
                mission_id,
                TimeUS,
                aligned_lat AS "Lat",
                aligned_lng AS "Lng",
                aligned_alt AS "RelHomeAlt",
                aligned_origin AS "RelOriginAlt",
                inode
            FROM fact_nav_state;
        """)

        # ---------------------------------------------------------
        # ✅ VALIDATION
        # ---------------------------------------------------------
        print("\n🧪 System Verification:")
        tables = conn.execute("SHOW TABLES").fetchall()
        print(f"  -> Total Tables/Views: {len(tables)}")

        cols = conn.execute("DESCRIBE view_nav_monitor").fetchall()
        for col in cols:
            print(f"  -> UI Column: {col[0]} ({col[1]})")

    except Exception as e:
        print(f"💥 Deployment Failed: {e}")
    finally:
        conn.close()
        print(f"\n🏁 Warehouse Ready: {DB_PATH}")

if __name__ == "__main__":
    main()
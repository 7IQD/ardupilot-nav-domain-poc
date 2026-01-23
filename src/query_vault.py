import duckdb
import pandas as pd

# Path to your Silver Vault
DB_PATH = "bin/nav_domain.db"

def get_recent_telemetry(limit=10):
    # Connect in read-only mode so it doesn't lock the database
    # while the main pipeline is running
    conn = duckdb.connect(DB_PATH, read_only=True)

    try:
        # Query the Gold View (v_nav_scaled)
        query = f"""
            SELECT
                inode,
                lat,
                lon,
                alt_m,
                rel_alt_m
            FROM v_nav_scaled
            ORDER BY inode DESC
            LIMIT {limit};
        """

        # Convert directly to a Pandas DataFrame
        df = conn.execute(query).df()
        return df

    except Exception as e:
        print(f"❌ Query Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("🛰️ Fetching latest Navigation data...")
    data = get_recent_telemetry()

    if not data.empty:
        print(data.to_string(index=False))
    else:
        print("📭 No data found in the vault.")
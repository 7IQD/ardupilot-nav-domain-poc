import os
import duckdb
import pandas as pd

"""
NavDataService — Primary DAO for the NAV Domain
Final Production State: Registry-driven, Type-safe, and Path-consistent.
"""

class NavDataService:

    def __init__(self, mission_id="MASTER_MISSION"):
        self.mission_id = mission_id
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.abspath(os.path.join(self.script_dir, "../../../"))
        self.registry_path = os.path.join(
            self.project_root,
            "src/df_domain_data_services/nav/nav_registry.duckdb"
        )

    def fetch_fused_telemetry(self) -> pd.DataFrame:
        if not os.path.exists(self.registry_path):
            return pd.DataFrame()

        # --- STEP 1: Get Shard Paths ---
        con = duckdb.connect(self.registry_path)
        path_results = con.execute(f"""
            SELECT shard_path FROM nav_registry WHERE mission_id = '{self.mission_id}'
        """).fetchall()
        con.close()

        paths = [p[0] for p in path_results if p[0]]
        if not paths:
            return pd.DataFrame()

        # ✅ FIX 1: Convert Python list to DuckDB-compatible string list
        # Result format: "['path/to/A.parquet', 'path/to/B.parquet']"
        path_str = "[" + ",".join([f"'{p}'" for p in paths]) + "]"

        # --- STEP 2: Registry-Driven Parquet Load ---
        con = duckdb.connect(database=":memory:")
        query = f"""
            SELECT
                TimeUS, Lat, Lng, Alt, Spd,
                NSats, HDop,
                Roll, Pitch, Yaw,
                VN, VE, VD, RelHomeAlt
            FROM read_parquet({path_str})
            WHERE Lat != 0 AND Lng != 0
        """
        df = con.execute(query).df()
        con.close()

        if df.empty:
            return df

        # --- STEP 3: Integrity & Cleaning ---
        numeric_cols = ["Lat","Lng","Alt","Spd","NSats","HDop","Roll","Pitch","Yaw","VN","VE","VD","RelHomeAlt"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        if "HDop" in df.columns:
            df["HDop"] = df["HDop"].clip(lower=0, upper=10)

        return df.sort_values("TimeUS").drop_duplicates("TimeUS").reset_index(drop=True)

    def get_state_report(self, mission_id=None) -> pd.DataFrame:
        if mission_id: self.mission_id = mission_id
        df = self.fetch_fused_telemetry()
        if not df.empty:
            df["mission_time"] = (df["TimeUS"] - df["TimeUS"].min()) / 1e6
        return df

    def get_summary(self, df: pd.DataFrame = None) -> dict:
        df = df if df is not None else self.fetch_fused_telemetry()
        if df.empty:
            return {"health_status": "RED", "error": "No data"}

        avg_hdop = df["HDop"].mean() if "HDop" in df.columns else None

        if avg_hdop is None:
            status = "UNKNOWN"
        elif avg_hdop < 1.5:
            status = "GREEN"
        elif avg_hdop < 3.0:
            status = "YELLOW"
        else:
            status = "RED"

        return {
            "health_status": status,
            # ✅ FIX 2: Correct Falsy Check (Allows 0.0 HDOP)
            "avg_hdop": round(avg_hdop, 2) if avg_hdop is not None else None,
            "row_count": len(df),
            "mission_id": self.mission_id
        }
import os
import duckdb
import pandas as pd

"""
NavDataService — Primary DAO for the NAV Domain
Responsibilities
- Load NAV warehouse parquet
- Filter invalid GPS coordinates
- Ensure TimeUS ordering
- Provide lightweight mission health summary

This layer MUST NOT perform feature engineering or labeling.
"""

class NavDataService:

    def __init__(self, mission_id=None):
        self.mission_id = mission_id

        # Resolve project root
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.abspath(os.path.join(self.script_dir, "../../../"))

        self.warehouse_path = os.path.join(
            self.project_root,
            "bin/vault/warehouse_df/nav_df_master.parquet"
        )

    def fetch_fused_telemetry(self) -> pd.DataFrame:

        if not os.path.exists(self.warehouse_path):
            print(f"Warehouse missing: {self.warehouse_path}")
            return pd.DataFrame()

        con = duckdb.connect(database=":memory:")

        query = f"""
            SELECT
                TimeUS,
                Lat,
                Lng,
                Alt,
                Spd,
                NSats,
                HDop,
                Roll,
                Pitch,
                Yaw,
                VN,
                VE,
                VD,
                RelHomeAlt
            FROM read_parquet('{self.warehouse_path}')
            WHERE Lat != 0 AND Lng != 0
        """

        df = con.execute(query).df()
        con.close()

        if df.empty:
            return df

        # Ensure numeric consistency
        numeric_cols = [
            "Lat","Lng","Alt","Spd","NSats","HDop",
            "Roll","Pitch","Yaw","VN","VE","VD","RelHomeAlt"
        ]

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Fix SITL HDOP anomaly
        if "HDop" in df.columns:
            df["HDop"] = df["HDop"].clip(lower=0, upper=10)

        # Ensure time ordering
        df = df.sort_values("TimeUS").drop_duplicates("TimeUS")

        return df


    def get_state_report(self, mission_id=None) -> pd.DataFrame:

        if mission_id:
            self.mission_id = mission_id

        df = self.fetch_fused_telemetry()

        if df.empty:
            return df

        start_ts = df["TimeUS"].min()
        df["mission_time"] = (df["TimeUS"] - start_ts) / 1e6

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
            "avg_hdop": round(avg_hdop, 2) if avg_hdop else None,
            "row_count": len(df)
        }


if __name__ == "__main__":
    service = NavDataService()
    df = service.get_state_report()
    summary = service.get_summary(df)

    print(f"✅ Loaded {len(df)} rows")
    print("Health Summary:", summary)
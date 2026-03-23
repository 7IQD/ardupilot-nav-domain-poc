import os
import pandas as pd
from src.utils.metrics_helpers import normalize_inverse, compute_stability_score

"""
NavStatsEngine
Purpose:
- Compute NAV performance metrics (Drift, Stability)
- Generate ML-ready feature set
- Bridge statistical results to the NavVerdictMap for health scoring
"""

class NavStatsEngine:

    @staticmethod
    def calculate_metrics(df):
        """
        Calculates P95 Drift, Stability, and HDOP averages.
        """

        if df is None or df.empty:
            return {
                "p95_drift": 0.0,
                "stability_score": 0.0,
                "nav_score": 0.0,
                "total_score": 0.0,
                "avg_hdop": None,
                "sample_count": 0
            }

        # ------------------------------------------------
        # 1. ALTITUDE DRIFT
        # ------------------------------------------------
        if "RelHomeAlt" in df.columns:
            alt_series = df["RelHomeAlt"].dropna()
        else:
            alt_series = pd.Series()

        if alt_series.empty:
            p95_drift = 0.0
        else:
            start_alt = alt_series.iloc[0]
            alt_error = (alt_series - start_alt).abs()
            p95_drift = float(alt_error.quantile(0.95))

        nav_score = normalize_inverse(p95_drift, worst=15.0, best=0.0)

        # ------------------------------------------------
        # 2. STABILITY
        # ------------------------------------------------
        df_stable = compute_stability_score(df, cols=["Roll", "Pitch"])

        stability_cols = [
            c for c in ["roll_stability", "pitch_stability"]
            if c in df_stable.columns
        ]

        if stability_cols:
            avg_stability = df_stable[stability_cols].mean().mean()
        else:
            avg_stability = 0.0

        # ------------------------------------------------
        # 3. HDOP (FINAL FIX)
        # ------------------------------------------------
        avg_hdop = df["HDop"].mean() if "HDop" in df.columns else None

        # ------------------------------------------------
        # 4. FINAL SCORE
        # ------------------------------------------------
        total_score = (nav_score + avg_stability) / 2

        return {
            "p95_drift": round(float(p95_drift), 3),
            "stability_score": round(float(avg_stability), 2),
            "nav_score": round(float(nav_score), 2),
            "total_score": round(float(total_score), 2),
            "avg_hdop": round(float(avg_hdop), 2) if pd.notna(avg_hdop) else None,
            "sample_count": len(df)
        }

    @staticmethod
    def generate_features(df):
        """
        FEATURE GENERATION FOR ML DATASET
        """

        if df is None or df.empty:
            return pd.DataFrame()

        features = {}

        if "Spd" in df.columns:
            features["speed_mean"] = df["Spd"].mean()
            features["speed_std"] = df["Spd"].std()

        if "NSats" in df.columns:
            features["sat_mean"] = df["NSats"].mean()
            features["sat_min"] = df["NSats"].min()

        if "HDop" in df.columns:
            features["hdop_mean"] = df["HDop"].mean()
            features["hdop_max"] = df["HDop"].max()

        if "Alt" in df.columns:
            features["alt_range"] = df["Alt"].max() - df["Alt"].min()

        if {"VN", "VE", "VD"}.issubset(df.columns):
            vel_mag = (df["VN"]**2 + df["VE"]**2 + df["VD"]**2) ** 0.5
            features["velocity_mean"] = vel_mag.mean()
            features["velocity_std"] = vel_mag.std()

        return pd.DataFrame([features])


if __name__ == "__main__":
    from .nav_data_service import NavDataService

    service = NavDataService()
    raw_df = service.get_state_report()

    if not raw_df.empty:
        stats = NavStatsEngine.calculate_metrics(raw_df)
        ml_features = NavStatsEngine.generate_features(raw_df)

        print("--- Mission Stats (Verdict Ready) ---")
        print(stats)
        print("\n--- ML Fingerprint ---")
        print(ml_features)
    else:
        print("Data Warehouse empty. Run ingestion first.")
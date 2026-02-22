# src/dashboard/nav/nav_stats.py
import pandas as pd
import numpy as np

class NavStatsEngine:
    @staticmethod
    def calculate_metrics(df):
        if df is None or df.empty:
            return {"p95_drift": 0, "max_drift": 0, "avg_hdop": 0, "sample_count": 0}

        # 🏛️ ARCHITECTURAL LOCK: Use exact DuckDB casing
        # Vertical Drift = |RelHomeAlt - RelOriginAlt|
        df['alt_error'] = (df['RelHomeAlt'] - df['RelOriginAlt']).abs()

        p95_drift = df['alt_error'].quantile(0.95)
        max_drift = df['alt_error'].max()
        avg_hdop = df['HDop'].mean() if 'HDop' in df.columns else 0.0

        # Breach timing (First instance > 1.5m)
        breach_rows = df[df['alt_error'] > 1.5]
        first_breach = breach_rows['mission_time'].iloc[0] if not breach_rows.empty else None

        return {
            "p95_drift": round(float(p95_drift), 3),
            "max_drift": round(float(max_drift), 3),
            "avg_hdop": round(float(avg_hdop), 2),
            "breach_time": first_breach,
            "sample_count": len(df)
        }
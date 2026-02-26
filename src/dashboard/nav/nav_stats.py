import pandas as pd
import numpy as np

class NavStatsEngine:
    @staticmethod
    def calculate_metrics(df):
        if df is None or df.empty:
            return {"p95_drift": 0.0, "max_drift": 0.0, "avg_hdop": 0.0, "score": 0.0}

        # Calculate error relative to the Truth (Gold Layer)
        df['alt_error'] = (df['RelHomeAlt'] - df['RelOriginAlt']).abs()

        p95_drift = float(df['alt_error'].quantile(0.95))
        max_drift = float(df['alt_error'].max())
        avg_hdop = float(df['HDop'].mean()) if 'HDop' in df.columns else 0.0

        # Scoring against the 1.5m soft-limit
        threshold = 1.5
        score_val = max(0, 100 * (1 - (p95_drift / threshold)))

        return {
            "p95_drift": round(p95_drift, 3),
            "max_drift": round(max_drift, 3),
            "avg_hdop": round(avg_hdop, 2),
            "score": round(score_val, 2),
            "sample_count": len(df)
        }
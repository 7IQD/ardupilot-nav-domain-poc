# nav_verdict_map.py

class NavVerdictMap:
    THRESHOLDS = {
        "alt_drift_critical": 1.5,
        "alt_drift_warning": 0.8,
        "hdop_good": 1.2
    }

    @classmethod
    def evaluate(cls, stats):

        p95 = stats.get('p95_drift', 0.0)
        avg_hdop = stats.get('avg_hdop')

        # ✅ FIX: Safe formatting
        hdop_str = f"{avg_hdop:.2f}" if avg_hdop is not None else "N/A"

        if stats.get('sample_count', 0) < 10:
            return {
                "verdict": "UNKNOWN",
                "score": 0,
                "status": "INCOMPLETE",
                "message": "⚠️ Insufficient data."
            }

        if p95 >= cls.THRESHOLDS["alt_drift_critical"]:
            verdict, score, status = "FAIL", 30, "CRITICAL"
        elif p95 >= cls.THRESHOLDS["alt_drift_warning"]:
            verdict, score, status = "WARNING", 70, "DEGRADED"
        else:
            verdict, score, status = "PASS", 100, "HEALTHY"

        msg = f"P95 Drift: {p95:.2f}m | HDOP: {hdop_str}"

        if verdict == "FAIL":
            msg += " — 🚨 Safety violation! Check EKF tuning."

        return {
            "verdict": verdict,
            "score": score,
            "status": status,
            "message": msg
        }
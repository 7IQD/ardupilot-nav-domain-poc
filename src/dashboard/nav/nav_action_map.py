# src/dashboard/nav/nav_action_map.py

class NavActionMap:
    """
    Mentor-grade NAV evaluation mapping.
    Evaluates altitude drift against thresholds and returns structured verdict, score, and status.
    """

    # Safety thresholds (ArduPilot standards)
    THRESHOLDS = {
        "alt_drift_critical": 1.5,
        "alt_drift_warning": 0.8,
        "hdop_good": 1.2
    }

    @classmethod
    def evaluate(cls, stats):
        """
        Evaluate mission stats and return a mentor-grade verdict.
        Returns:
            dict: {
                "verdict": PASS/WARNING/FAIL,
                "score": 0-100,
                "status": CRITICAL/DEGRADED/HEALTHY,
                "message": executive summary string
            }
        """
        p95 = stats.get('p95_drift', None)
        avg_hdop = stats.get('avg_hdop', None)

        if p95 is None:
            return {
                "verdict": "UNKNOWN",
                "score": 0,
                "status": "UNKNOWN",
                "message": "⚠️ Insufficient data to evaluate altitude drift."
            }

        # Determine verdict & status
        if p95 >= cls.THRESHOLDS["alt_drift_critical"]:
            verdict, score, status = "FAIL", 30, "CRITICAL"
        elif p95 >= cls.THRESHOLDS["alt_drift_warning"]:
            verdict, score, status = "WARNING", 70, "DEGRADED"
        else:
            verdict, score, status = "PASS", 100, "HEALTHY"

        # Mentor-grade message
        message = f"P95 Drift: {p95:.3f} m"
        if avg_hdop is not None:
            message += f" | Avg HDOP: {avg_hdop:.2f}"
        if verdict == "FAIL":
            message += " — Exceeds safety threshold. Inspect control tuning."
        elif verdict == "WARNING":
            message += " — Approaching critical drift. Monitor closely."
        else:
            message += " — Within safe limits."

        return {
            "verdict": verdict,
            "score": score,
            "status": status,
            "message": message
        }
"""
dashboard_ekf.py
----------------
EKF Health Dashboard (Read-Only)
Directly utilizes DatabaseManager to bypass obsolete query_vault.
"""

from typing import Dict, Any
from data_mart_engine.database_manager import DatabaseManager

# Metrics aligned with the fact_nav_precision table columns we just verified
EKF_METRICS = [
    "timestamp",
    "ekf_healthy",
    "vel_variance",
    "pos_variance"
]

def load_ekf_snapshot(limit: int = 1) -> Dict[str, Any]:
    """
    Pull latest EKF state from the Gold Vault using DatabaseManager.
    """
    db = DatabaseManager()

    metrics_str = ", ".join(EKF_METRICS)
    query = f"SELECT {metrics_str} FROM fact_nav_precision ORDER BY timestamp DESC LIMIT {limit}"

    try:
        df = db.query_gold(query)
    except Exception as e:
        return {
            "status": "ERROR",
            "message": str(e),
            "timestamp": None,
            "ekf": None,
        }

    if df is None or df.empty:
        return {
            "status": "NO_DATA",
            "timestamp": None,
            "ekf": None,
        }

    latest = df.iloc[0]

    return {
        "status": "OK",
        "timestamp": latest.get("timestamp"),
        "ekf": {
            "healthy": bool(latest.get("ekf_healthy")),
            "status": "GOLD_STABLE",
            "variance": {
                "velocity": latest.get("vel_variance"),
                "position": latest.get("pos_variance"),
            }
        },
    }

def render_cli(snapshot: Dict[str, Any]) -> None:
    """
    Renders the EKF metrics to the console.
    """
    print("\n" + "═"*40)
    print("  🚀 ARDUPILOT EKF HEALTH DASHBOARD  ")
    print("═"*40)
    print(f" Timestamp:  {snapshot['timestamp']}")
    print(f" EKF Health: {'✅ HEALTHY' if snapshot['ekf']['healthy'] else '❌ UNHEALTHY'}")
    print(f" DB Status:  {snapshot['ekf']['status']}")
    print("-" * 40)
    print(" VARIANCE ANALYSIS:")
    print(f"  ▶ Velocity Variance: {snapshot['ekf']['variance']['velocity']:.6f}")
    print(f"  ▶ Position Variance: {snapshot['ekf']['variance']['position']:.6f}")
    print("═"*40 + "\n")

if __name__ == "__main__":
    snap = load_ekf_snapshot()
    if snap["status"] == "OK":
        render_cli(snap)
    elif snap["status"] == "NO_DATA":
        print("📊 Dashboard: No Gold data found. Ensure 'nav_refinery' has been run.")
    else:
        print(f"❌ Dashboard Error: {snap.get('message')}")
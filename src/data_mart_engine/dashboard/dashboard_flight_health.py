from typing import Dict, Any
from src.data_mart_engine.database_manager import DatabaseManager

def load_flight_snapshot() -> Dict[str, Any]:
    db = DatabaseManager()
    
    # Updated queries to find the latest valid (non-zero/non-nan) data
    nav_query = "SELECT timestamp, ekf_healthy, vel_variance, pos_variance FROM fact_nav_precision WHERE vel_variance IS NOT NULL ORDER BY timestamp DESC LIMIT 1"
    sys_query = "SELECT voltage, current, cpu_load FROM fact_sys_status WHERE voltage > 0 ORDER BY timestamp DESC LIMIT 1"
    
    try:
        nav_df = db.query_gold(nav_query)
        sys_df = db.query_gold(sys_query)
        
        if nav_df.empty or sys_df.empty:
            return {"status": "NO_DATA"}

        nav = nav_df.iloc[0]
        sys = sys_df.iloc[0]

        return {
            "status": "OK",
            "timestamp": nav['timestamp'],
            "nav": {"healthy": bool(nav['ekf_healthy']), "vel_var": nav['vel_var'], "pos_var": nav['pos_var']} if 'vel_var' in nav else {"healthy": bool(nav['ekf_healthy']), "vel_var": nav['vel_variance'], "pos_var": nav['pos_variance']},
            "sys": {"voltage": sys['voltage'], "current": sys['current'], "load": sys['cpu_load']}
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

def render_cli(snap: Dict[str, Any]):
    print("\n" + "═"*45)
    print(" 🚁 UNIFIED FLIGHT SYSTEM HEALTH 🚀 ")
    print("═"*45)
    print(f" Timestamp:  {snap['timestamp']}")
    print("\n [ NAVIGATION DOMAIN ]")
    print(f"  EKF Status:   {'✅ HEALTHY' if snap['nav']['healthy'] else '❌ UNHEALTHY'}")
    print(f"  Vel Variance: {snap['nav']['vel_var']:.6f}")
    print("\n [ SYSTEM DOMAIN ]")
    v = snap['sys']['voltage']
    volt_icon = "🔋" if v > 12.0 else "⚠️"
    print(f"  Battery:      {volt_icon} {v:.2f} V")
    print(f"  Current:      {snap['sys']['current']:.2f} A")
    print(f"  CPU Load:     {snap['sys']['load']:.1f} %")
    print("═"*45 + "\n")

if __name__ == "__main__":
    snapshot = load_flight_snapshot()
    if snapshot["status"] == "OK":
        render_cli(snapshot)
    else:
        print(f"📊 Dashboard: {snapshot['status']}. Ensure refineries have run and data is valid.")

#!/usr/bin/env python3
from src.core.domain_marts.nav_reliability import refresh_nav_mart
from src.core.domain_marts.sys_reliability import refresh_sys_mart
from src.core.domain_marts.power_health import refresh_power_mart
from src.core.domain_marts.est_accuracy import refresh_est_mart
from src.core.domain_marts.com_link import refresh_com_mart

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DB_PATH = ROOT / "bin/vault/warehouse_df/drone_df_views.db"

def refresh_all_marts(mission_id=None, domains=None):
    """
    Orchestrates refresh of all five domain service marts in DF path.
    mission_id: optional, to refresh only a specific flight
    domains: list of domains to refresh; defaults to all five
    """
    domains = domains or ["NAV", "SYS", "POWER", "EST", "COM"]
    print("📢 Starting DF Path Mart Refresh...")
    print(f"Target DB: {DB_PATH}")
    print(f"Domains to refresh: {domains}")
    print(f"Mission filter: {mission_id if mission_id else 'ALL'}")

    for domain in domains:
        try:
            print(f"\n🔄 Refreshing {domain} Mart...")
            if domain == "NAV":
                refresh_nav_mart(DB_PATH, mission_id)
            elif domain == "SYS":
                refresh_sys_mart(DB_PATH, mission_id)
            elif domain == "POWER":
                refresh_power_mart(DB_PATH, mission_id)
            elif domain == "EST":
                refresh_est_mart(DB_PATH, mission_id)
            elif domain == "COM":
                refresh_com_mart(DB_PATH, mission_id)
            else:
                print(f"⚠️ Unknown domain: {domain}")
        except Exception as e:
            print(f"❌ Error refreshing {domain} Mart: {e}")

    print("\n✅ All requested domain marts refreshed.")

if __name__ == "__main__":
    # Example: refresh all domains for all missions
    refresh_all_marts()

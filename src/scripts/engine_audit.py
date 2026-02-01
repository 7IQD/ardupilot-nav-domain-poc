import pandas as pd
import os

def run_rock_solid_audit():
    nav_path = 'bin/vault/warehouse/nav_master.parquet'
    sys_path = 'bin/vault/warehouse/sys_master.parquet'

    if not os.path.exists(nav_path) or not os.path.exists(sys_path):
        print("❌ Error: Master parquet files not found. Run the engine first.")
        return

    print("🚀 Starting Engine Integrity Stress Test...\n")
    nav = pd.read_parquet(nav_path)
    sys = pd.read_parquet(sys_path)

    print("--- 1. GHOST FIELD AUDIT (Missing Data) ---")
    critical_nav = ['lat', 'lon', 'roll', 'pitch', 'alt']
    existing_nav = [f for f in critical_nav if f in nav.columns]
    null_report = nav[existing_nav].isnull().mean() * 100
    for field, val in null_report.items():
        status = "✅" if val < 5 else "⚠️"
        print(f"{status} {field}: {val:.2f}% null")
    print("")

    print("--- 2. CLOCK DRIFT & LATENCY ---")
    if 'time_boot_ms' in nav.columns and 'wall_ns' in nav.columns:
        wall_ms = (nav['wall_ns'] - nav['wall_ns'].min()) / 1e6
        boot_ms = nav['time_boot_ms'] - nav['time_boot_ms'].min()
        latency_drift = wall_ms - boot_ms
        print(f"✅ Avg Processing Latency: {latency_drift.mean():.2f} ms")
        print(f"✅ Jitter (Std Dev):       {latency_drift.std():.2f} ms")
        if latency_drift.max() > 500:
            print(f"⚠️ High Latency Spike detected ({latency_drift.max():.2f} ms)")
    else:
        print("ℹ️ Clock Drift: Skipped (time_boot_ms missing in Nav)")
    print("")

    print("--- 3. SCHEMA UTILIZATION (Message Gating) ---")
    if 'mavpackettype' in nav.columns:
        pivot = nav.groupby('mavpackettype').size()
        print("Records per Message Type:")
        print(pivot)
    print("")

    print("--- 4. HZ STABILITY (Throughput) ---")
    sys['arrival_sec'] = (sys['wall_ns'] - sys['wall_ns'].min()) // 1e9
    hz_stability = sys.groupby('arrival_sec').size()
    avg_hz = hz_stability.mean()
    min_hz = hz_stability.min()
    print(f"✅ Average Throughput: {avg_hz:.2f} pkts/sec")
    if min_hz < (avg_hz * 0.5):
        print(f"⚠️ Throughput dropped to {min_hz} pkts/sec at some point.")
    else:
        print(f"✅ Flow Consistency: Stable")

    print("\n🏁 --- AUDIT COMPLETE ---")

if __name__ == "__main__":
    run_rock_solid_audit()

#!/usr/bin/env python3
import os
import duckdb

# --- PATHS ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))
WAREHOUSE_DF = os.path.join(PROJECT_ROOT, "bin/vault/warehouse_df")
VAULT_DB = os.path.join(WAREHOUSE_DF, "drone_df_views.db")

# --- CONNECT TO VAULT ---
con = duckdb.connect(VAULT_DB)

# --- CREATE VIEWS ---
# Navigation
con.execute("""
CREATE OR REPLACE VIEW fact_navigation AS
SELECT * FROM parquet_scan('nav_df_master.parquet')
""")

# Estimator
con.execute("""
CREATE OR REPLACE VIEW fact_estimator AS
SELECT * FROM parquet_scan('est_df_master.parquet')
""")

# System
con.execute("""
CREATE OR REPLACE VIEW fact_system AS
SELECT * FROM parquet_scan('sys_df_master.parquet')
""")

# Power
con.execute("""
CREATE OR REPLACE VIEW fact_power AS
SELECT * FROM parquet_scan('power_df_master.parquet')
""")

# Communication
con.execute("""
CREATE OR REPLACE VIEW fact_communication AS
SELECT * FROM parquet_scan('com_df_master.parquet')
""")

# -----------------------------
# Analytical / Diagnostic Views
# -----------------------------

# NAV Example: telemetry attitude
con.execute("""
CREATE OR REPLACE VIEW view_telemetry_attitude AS
SELECT timestamp, roll, pitch, yaw
FROM fact_navigation
""")

# NAV Example: perspective delta
con.execute("""
CREATE OR REPLACE VIEW view_perspective_delta AS
SELECT timestamp, lat, lon, alt, prev_lat, prev_lon, prev_alt,
       (lat - prev_lat) AS delta_lat,
       (lon - prev_lon) AS delta_lon,
       (alt - prev_alt) AS delta_alt
FROM fact_navigation
""")

# SYS Example: system vibration stress
con.execute("""
CREATE OR REPLACE VIEW view_system_vibe_stress AS
SELECT timestamp, VibeX, VibeY, VibeZ
FROM fact_system
""")

# POWER Example: battery voltage drop rate
con.execute("""
CREATE OR REPLACE VIEW view_power_health AS
SELECT timestamp, volt, (volt - LAG(volt) OVER (ORDER BY timestamp)) AS v_drop_rate
FROM fact_power
""")

# COM Example: radio & RC link quality
con.execute("""
CREATE OR REPLACE VIEW view_comm_link_quality AS
SELECT
    timestamp AS timestamp_sec,
    COALESCE(RSSI, RemRSSI) AS signal_strength,
    Noise AS noise_floor,
    (COALESCE(RSSI, RemRSSI) - Noise) AS signal_to_noise_ratio,
    mavpackettype
FROM fact_communication
WHERE mavpackettype IN ('RAD', 'RCIN')
      AND (RSSI IS NOT NULL OR RemRSSI IS NOT NULL)
""")

print(f"✅ All views created successfully in: {VAULT_DB}")

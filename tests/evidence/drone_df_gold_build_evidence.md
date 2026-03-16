# Drone DF Gold Build Evidence Report

**Generated on:** 2026-03-04 04:42:42 UTC\
**Database:** bin/vault/drone_df_views.db

------------------------------------------------------------------------

## 1. Available Fact Tables

-   fact_nav_state_vector\
-   fact_est_state_vector\
-   fact_power_state_vector\
-   fact_com_state_vector\
-   fact_sys_state_vector\
-   fact_flight_diagnostics (Fusion View)

------------------------------------------------------------------------

## 2. Fusion View Schema (fact_flight_diagnostics)

  Column       Type
  ------------ ---------
  mission_id   VARCHAR
  TimeUS       BIGINT
  Lat          DOUBLE
  Lng          DOUBLE
  Alt          DOUBLE
  spd_gps      DOUBLE
  Roll         DOUBLE
  Pitch        DOUBLE
  Yaw          DOUBLE
  Volt         DOUBLE
  Curr         DOUBLE
  EnrgTot      INTEGER
  RSSI         DOUBLE
  RemRSSI      DOUBLE
  cpu_load     BIGINT
  mem_free     BIGINT

------------------------------------------------------------------------

## 3. Domain Table Schemas

### NAV (fact_nav_state_vector)

-   mission_id (VARCHAR)
-   TimeUS (BIGINT)
-   Lat (DOUBLE)
-   Lng (DOUBLE)
-   Alt (DOUBLE)
-   spd_gps (DOUBLE)

### EST (fact_est_state_vector)

-   mission_id (VARCHAR)
-   TimeUS (BIGINT)
-   Roll (DOUBLE)
-   Pitch (DOUBLE)
-   Yaw (DOUBLE)

### POWER (fact_power_state_vector)

-   mission_id (VARCHAR)
-   TimeUS (BIGINT)
-   Volt (DOUBLE)
-   Curr (DOUBLE)
-   EnrgTot (INTEGER)

### COM (fact_com_state_vector)

-   mission_id (VARCHAR)
-   TimeUS (BIGINT)
-   RSSI (DOUBLE)
-   RemRSSI (DOUBLE)

### SYS (fact_sys_state_vector)

-   mission_id (VARCHAR)
-   TimeUS (BIGINT)
-   cpu_load (BIGINT)
-   mem_free (BIGINT)

------------------------------------------------------------------------

## 4. Validation Statement

All five operational domains (NAV, EST, POWER, COM, SYS) are
materialized as fact tables.\
The unified fusion view `fact_flight_diagnostics` is anchored on NAV and
ASOF-joined across all other domains using (mission_id, TimeUS).

This confirms:

-   Single mission_id consistency across domains\
-   Time-synchronized multi-domain fusion\
-   Clean Gold Build state aligned with source BIN ingestion

------------------------------------------------------------------------

**Status:** ✅ Gold Layer Ready for Domain Analysis

# DataFlash Processing Pipeline

## Flow

```text
BIN → pymavlink → parquet shards → ingest_nav_msn → nav_master → DuckDB
```

---

## DF Domain-Segregated Parquet Structure

```text
Logs/
 ├── <mission>.BIN
 ├── vaul(extracted and domain segregated)/
 │    ├── nav_domain_shard_*.parquet
 │    ├── est_domain_shard_*.parquet
 │    ├── power_domain_shard_*.parquet
 │    ├── com_domain_shard_*.parquet
 │    ├── sys_domain_shard_*.parquet
 │
```

Each domain (NAV, EST, POWER, COM, SYS, etc.) follows the same sharding pattern.

These domain-specific parquet shards are the standardized input for building respective domain masters (e.g., nav_master).

---

## DF Storage Layers

```text
df_source/
  → Raw BIN logs (per test case, e.g. T1_GPS_LOSS_RUN01.BIN)

vault_b/
  → Extracted parquet shards (organized per mission/test, e.g. T1/)

warehouse_df/
  → DuckDB warehouse
     → nav_master
     → nav_windows
     → NAV analysis tables
```

Data flows strictly in one direction:

```text
BIN → shards → warehouse (analysis-ready)
```

---

## Steps

1. BIN logs are parsed using pymavlink
2. Data is split into domain-specific parquet shards (standardized across all domains)
3. Shards are stored without modification
4. Domain master tables (e.g., nav_master) are built by merging shards and assigning a mission_id
6. DuckDB is used for query execution and analysis

---

## NAV Master Construction

```text
nav_master =
  union(all NAV shards)
  + mission_id (per ingestion batch)
```

Each ingestion run assigns a unique `mission_id`, enabling:

* mission-level grouping
* RCA traceability
* consistent downstream analysis

---

## Design

* Sharding enables scalable ingestion
* Raw telemetry is preserved
* DuckDB enables fast and reproducible queries

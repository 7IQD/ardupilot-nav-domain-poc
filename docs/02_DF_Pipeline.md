# DataFlash Processing Pipeline

## Flow

BIN → pymavlink → parquet shards → nav_segment_* → nav_master → DuckDB

## Steps

1. BIN logs are parsed using pymavlink
2. Data is split into domain-specific parquet shards
3. Shards are stored without modification
4. NAV domain data is combined into nav_segment tables
5. nav_master is built for mission-level analysis
6. DuckDB is used for query execution and analysis

## Design

- Sharding enables scalable ingestion
- Raw telemetry is preserved
- DuckDB enables fast and reproducible queries
#!/bin/bash
# create_domain_master_db.sh
# Stage-1 Refinery: Raw-to-Structured Ingress (NAV Domain)

INGRESS_DIR="../../bin/vault/vault_b"
WAREHOUSE_DIR="../../bin/vault/warehouse_df"

# Mission ID from first shard
FIRST_SHARD=$(ls $INGRESS_DIR/nav_domain_shard_*.parquet 2>/dev/null | head -n 1)

if [ -n "$FIRST_SHARD" ]; then
    STR_TIME=$(basename "$FIRST_SHARD" | grep -oP '\d{10}' | head -n 1)
    MISSION_ID="NAV_$(date -d @${STR_TIME} +%Y%m%d_%H%M)"
else
    MISSION_ID="NAV_$(date +%Y%m%d_%H%M)_SYS"
fi

echo "[Refinery] Starting NAV Master Creation"
echo "Mission ID: $MISSION_ID"

# Spill space setup
rm -rf /tmp/duckdb_spill
mkdir -p /tmp/duckdb_spill

# DuckDB streaming execution (no staging table)
duckdb -c "
PRAGMA memory_limit='4GB';
PRAGMA temp_directory='/tmp/duckdb_spill';

COPY (
    SELECT
        *,
        '$MISSION_ID' AS mission_id,
        (abs(TimeUS) % 5) + 1 AS segment_id
    FROM read_parquet('$INGRESS_DIR/nav_domain_shard_*.parquet', union_by_name=True)
)
TO '$WAREHOUSE_DIR/${MISSION_ID}_parts'
(FORMAT PARQUET, PARTITION_BY (segment_id));

"

echo "[Done] NAV warehouse created at:"
echo "$WAREHOUSE_DIR/${MISSION_ID}_parts/"
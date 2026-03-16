## NAV Data Capture

1. NAV Domain
duckdb -c "DESCRIBE SELECT * FROM 'nav_df_master.parquet';"

─────────────┬─────────────┬─────────┬─────────┬─────────┬─────────┐
│  column_name  │ column_type │  null   │   key   │ default │  extra  │
├───────────────┼─────────────┼─────────┼─────────┼─────────┼─────────┤
│ TimeUS        │ BIGINT      │ YES     │         │         │         │
│ Lat           │ DOUBLE      │ YES     │         │         │         │
│ Lng           │ DOUBLE      │ YES     │         │         │         │
│ Alt           │ DOUBLE      │ YES     │         │         │         │
│ Spd           │ DOUBLE      │ YES     │         │         │         │
│ NSats         │ DOUBLE      │ YES     │         │         │         │
│ HDop          │ DOUBLE      │ YES     │         │         │         │
│ Status        │ DOUBLE      │ YES     │         │         │         │
│ Roll          │ DOUBLE      │ YES     │         │         │         │
│ Pitch         │ DOUBLE      │ YES     │         │         │         │
│ Yaw           │ DOUBLE      │ YES     │         │         │         │
│ msg_type      │ VARCHAR     │ YES     │         │         │         │
│ inode         │ BIGINT      │ YES     │         │         │         │
│ wall_ns       │ BIGINT      │ YES     │         │         │         │
│ mavpackettype │ VARCHAR     │ YES     │         │         │         │
└───────────────┴─────────────┴─────────┴─────────┴─────────┴─────────┘

2.  Estimator Domain
duckdb -c "DESCRIBE SELECT * FROM 'est_df_master.parquet';"
┌───────────────┬─────────────┬─────────┬─────────┬─────────┬─────────┐
│  column_name  │ column_type │  null   │   key   │ default │  extra  │
├───────────────┼─────────────┼─────────┼─────────┼─────────┼─────────┤
│ TimeUS        │ BIGINT      │ YES     │         │         │         │
│ Roll          │ INTEGER     │ YES     │         │         │         │
│ Pitch         │ INTEGER     │ YES     │         │         │         │
│ Yaw           │ INTEGER     │ YES     │         │         │         │
│ VN            │ INTEGER     │ YES     │         │         │         │
│ VE            │ INTEGER     │ YES     │         │         │         │
│ VD            │ INTEGER     │ YES     │         │         │         │
│ VibeX         │ DOUBLE      │ YES     │         │         │         │
│ VibeY         │ DOUBLE      │ YES     │         │         │         │
│ VibeZ         │ DOUBLE      │ YES     │         │         │         │
│ Clip          │ DOUBLE      │ YES     │         │         │         │
│ GyrX          │ DOUBLE      │ YES     │         │         │         │
│ AccX          │ DOUBLE      │ YES     │         │         │         │
│ msg_type      │ VARCHAR     │ YES     │         │         │         │
│ inode         │ BIGINT      │ YES     │         │         │         │
│ wall_ns       │ BIGINT      │ YES     │         │         │         │
│ IMU           │ DOUBLE      │ YES     │         │         │         │
│ GH            │ DOUBLE      │ YES     │         │         │         │
│ GHz           │ DOUBLE      │ YES     │         │         │         │
└───────────────┴─────────────┴─────────┴─────────┴─────────┴─────────┘

3. System Domain
duckdb -c "DESCRIBE SELECT * FROM 'sys_df_master.parquet';"
┌───────────────┬─────────────┬─────────┬─────────┬─────────┬─────────┐
│  column_name  │ column_type │  null   │   key   │ default │  extra  │
├───────────────┼─────────────┼─────────┼─────────┼─────────┼─────────┤
│ TimeUS        │ BIGINT      │ YES     │         │         │         │
│ Load          │ BIGINT      │ YES     │         │         │         │
│ Mem           │ BIGINT      │ YES     │         │         │         │
│ KHz           │ INTEGER     │ YES     │         │         │         │
│ MaxT          │ BIGINT      │ YES     │         │         │         │
│ ErrL          │ BIGINT      │ YES     │         │         │         │
│ SPIC          │ BIGINT      │ YES     │         │         │         │
│ I2CC          │ BIGINT      │ YES     │         │         │         │
└───────────────┴─────────────┴─────────┴─────────┴─────────┴─────────┘

4. Power Domain
duckdb -c "DESCRIBE SELECT * FROM 'power_df_master.parquet';"

┌───────────────┬─────────────┬─────────┬─────────┬─────────┬─────────┐
│  column_name  │ column_type │  null   │   key   │ default │  extra  │
├───────────────┼─────────────┼─────────┼─────────┼─────────┼─────────┤
│ TimeUS        │ BIGINT      │ YES     │         │         │         │
│ Volt          │ DOUBLE      │ YES     │         │         │         │
│ Amp           │ INTEGER     │ YES     │         │         │         │
│ EnrgTot       │ DOUBLE      │ YES     │         │         │         │
│ Temp          │ DOUBLE      │ YES     │         │         │         │
│ msg_type      │ VARCHAR     │ YES     │         │         │         │
│ inode         │ BIGINT      │ YES     │         │         │         │
│ wall_ns       │ BIGINT      │ YES     │         │         │         │
│ VoltR         │ DOUBLE      │ YES     │         │         │         │
│ Curr          │ DOUBLE      │ YES     │         │         │         │
│ CurrTot       │ DOUBLE      │ YES     │         │         │         │
│ RemPct        │ BIGINT      │ YES     │         │         │         │
│ SH            │ BIGINT      │ YES     │         │         │         │
└───────────────┴─────────────┴─────────┴─────────┴─────────┴─────────┘
5. Communication Domain
duckdb -c "DESCRIBE SELECT * FROM 'com_df_master.parquet';"

┌───────────────┬─────────────┬─────────┬─────────┬─────────┬─────────┐
│  column_name  │ column_type │  null   │   key   │ default │  extra  │
├───────────────┼─────────────┼─────────┼─────────┼─────────┼─────────┤
│ TimeUS        │ BIGINT      │ YES     │         │         │         │
│ RSSI          │ INTEGER     │ YES     │         │         │         │
│ RemRSS        │ INTEGER     │ YES     │         │         │         │
│ TxPwr         │ INTEGER     │ YES     │         │         │         │
│ msg_type      │ VARCHAR     │ YES     │         │         │         │
│ inode         │ BIGINT      │ YES     │         │         │         │
│ wall_ns       │ BIGINT      │ YES     │         │         │         │
│ mavpackettype │ VARCHAR     │ YES     │         │         │         │
│ C1            │ BIGINT      │ YES     │         │         │         │
│ C2            │ BIGINT      │ YES     │         │         │         │
│ C3            │ BIGINT      │ YES     │         │         │         │
│ C4            │ BIGINT      │ YES     │         │         │         │
│ C5            │ BIGINT      │ YES     │         │         │         │
│ C6            │ BIGINT      │ YES     │         │         │         │
│ C7            │ BIGINT      │ YES     │         │         │         │
│ C8            │ BIGINT      │ YES     │         │         │         │
│ C9            │ BIGINT      │ YES     │         │         │         │
│ C10           │ BIGINT      │ YES     │         │         │         │
│ C11           │ BIGINT      │ YES     │         │         │         │
│ C12           │ BIGINT      │ YES     │         │         │         │
│ C13           │ BIGINT      │ YES     │         │         │         │
│ C14           │ BIGINT      │ YES     │         │         │         │
└───────────────┴─────────────┴─────────┴─────────┴─────────┴─────────┘
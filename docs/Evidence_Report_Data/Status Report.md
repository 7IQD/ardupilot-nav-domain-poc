# NAV Domain POC – Status 27 Mar 26

**NAV Processing Sequence:** BIN → FMT Decode → Domain Shards → NAV Segments → nav_master → Inode Traceability

### BIN → Domain Shards (Controlled Ingestion)
The Data Flash pipeline has been built to ingest raw .BIN file (`T1_GPS_LOSS_RUN01.BIN`). The file was generated in SITL by introducing a controlled, gradual GPS degradation. The number of visible satellites (NSats) was reduced in steps 12 → 7 → 3 → 0 → 12, simulating a realistic loss and recovery cycle. This creates a clear degradation window where GPS quality deteriorates before complete loss (NSats = 0) and then stabilizes again.

All the msg_types have been grouped into one of the five domains (NAV, EST, POWER, COM, SYS) and written as independent Parquet shards. The evidence shows successful ingestion and consistent shard generation across domains.

**[Image 1]**

### Processing: Shards → nav_segment_* → nav_master.duckdb
Shards generated from the BIN logs (stored as Parquet files per message type) are first organized into segment-wise tables (nav_segment_1 to nav_segment_5). These segmented tables are then consolidated into a single warehouse database, `nav_master.duckdb`, creating a unified and queryable structure that supports rule execution and enables reliable state reconstruction using inode-level traceability.

**[Image 2]**

The T1 GPS Loss anomaly as per the sequence 12 → 7 → 3 → 0 → 12 is correctly captured in the NAV data.

**[Image 3]**

### Rule Execution → Meta Log
Finally to conduct mission analysis of the nav domain, nav data profiling is done to tag the instance where rules are violated by the parameter in a sequential manner for Nav dataset (Segment 1-only). Valid hits are captured in the meta layer with inode, TimeUS, and actual values. The T1 run clearly detects GPS loss (N-1) with 267 events, while other rules are safely skipped due to controlled SITL run.

**[Image 4]**
# Runtime Execution Flow

1. Mission starts (manual or scripted)
2. Platform ingress writes to Silver Mart
3. Data Mart Engine pulses:
   - Reads latest Silver tail
   - Aligns asynchronous packets
   - Computes NAV geometry
4. Gold artifacts are written per product
5. Dashboards read Gold files
6. Human may capture evidence to Dashboard Vault

## Determinism
- No shared state between pulses
- Overwrite-by-design for Gold artifacts
- Silver remains immutable

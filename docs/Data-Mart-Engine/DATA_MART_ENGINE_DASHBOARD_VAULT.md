# Class & Function Interactions

## Primary Classes

### NavRefinery
Location: `refinery/nav_refinery.py`

Responsibilities:
- Load Silver Mart data
- Perform temporal alignment (ASOF)
- Compute geometric NAV errors
- Emit Gold Mart artifacts

### Engine Controller (main.py)
Responsibilities:
- Instantiate refinery per product
- Manage mission context
- Pulse execution deterministically

## Interaction Flow

main.py
  └── NavRefinery(mission_id, product_type)
        ├── reads: Silver Mart
        ├── computes: NAV deltas
        └── writes: Gold Mart

Dashboards never call the refinery.
Dashboards only read Gold artifacts.

import json
import time
import os

def seal_mission(mission_id, status="COMPLETED"):
    """
    Finalizes the mission by writing a human-readable manifest.
    This acts as the 'Certificate of Completion' for the Gold Warehouse.
    """
    manifest = {
        "mission_id": mission_id,
        "sealed_at_utc": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
        "timestamp_unix": time.time(),
        "status": status,
        "note": "POC CLOSED – DATA MARTS NEXT",
        "version": "1.0.0"
    }

    # Path logic follows the SSOT (Single Source of Truth) mission folder
    path = f"bin/vault/vault_c/{mission_id}/manifest.json"

    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(manifest, f, indent=2)
        print(f"📜 Manifest sealed: {path}")
    except Exception as e:
        print(f"❌ Failed to seal manifest: {e}")
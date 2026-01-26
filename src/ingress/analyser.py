import os
import json
import logging
from data_manager import DataManager

logging.basicConfig(
    filename='logs/integrity_audit.log',
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger("integrity_audit")

def run_integrity_audit(base_name="flight_test"):
    db = DataManager(base_name=base_name, folder="bin")
    bin_path = db.bin_path
    jsonl_path = db.jsonl_path

    logger.info(f"Starting Integrity Audit on {base_name}")

    if not os.path.exists(bin_path) or not os.path.exists(jsonl_path):
        logger.error("One or both files are missing!")
        return

    with open(jsonl_path, "r") as j:
        entries = [json.loads(l) for l in j if json.loads(l).get("inode") is not None]

    if not entries:
        logger.warning("Registry empty.")
        return

    last = entries[-1]
    expected_size = last["offset"] + last["length"]
    actual_size = os.path.getsize(bin_path)

    logger.info(f"Registry Depth: {last['inode']} packets")
    logger.info(f"Expected Bin Size: {expected_size} bytes | Actual Bin Size: {actual_size} bytes")

    if expected_size == actual_size:
        logger.info("✅ Lateral Lock confirmed. Bin and registry aligned.")
    else:
        logger.error("❌ BIN / REGISTRY MISALIGNMENT detected!")

if __name__ == "__main__":
    run_integrity_audit()

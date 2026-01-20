import os
import json
from data_manager import DataManager

def run_integrity_audit(base_name="flight_test"):
    db = DataManager(base_name="flight_test", folder="bin")
    bin_path = db.bin_path
    jsonl_path = db.jsonl_path

    print(f"--- Starting Integrity Audit on {base_name} ---")

    if not os.path.exists(bin_path) or not os.path.exists(jsonl_path):
        print("❌ Error: One or both files are missing!")
        return

    with open(jsonl_path, "r") as j:
        entries = [json.loads(l) for l in j if "inode" in l]

    if not entries:
        print("❓ Registry empty.")
        return

    last = entries[-1]
    expected_size = last["offset"] + last["length"]
    actual_size = os.path.getsize(bin_path)

    print(f"Registry Depth: {last['inode']} packets")
    print(f"Expected Bin Size: {expected_size} bytes")
    print(f"Actual Bin Size:   {actual_size} bytes")

    if expected_size == actual_size:
        print("✅ LATERAL LOCK confirmed.")
    else:
        print("❌ BIN / REGISTRY MISALIGNMENT.")

if __name__ == "__main__":
    run_integrity_audit()

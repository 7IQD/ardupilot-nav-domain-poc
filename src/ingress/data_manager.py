import os
import json

class DataManager:
    def __init__(self, base_name="flight_test", folder=None):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.folder = os.path.join(current_dir, folder) if folder else current_dir
        os.makedirs(self.folder, exist_ok=True)

        self.bin_path = os.path.join(self.folder, f"{base_name}.bin")
        self.jsonl_path = os.path.join(self.folder, f"{base_name}.jsonl")

        # 🔥 Hot-path state (no syscalls during capture)
        self.current_inode = 0
        self.current_offset = 0

    def initialize_storage(self, overwrite=False):
        if overwrite:
            open(self.bin_path, "wb").close()
            open(self.jsonl_path, "w").close()
            self.current_inode = 0
            self.current_offset = 0
        else:
            # Resume safely
            self.current_offset = os.path.getsize(self.bin_path)

    def write_entry(self, raw_bytes: bytes):
        length = len(raw_bytes)

        record = {
            "inode": self.current_inode + 1,
            "offset": self.current_offset,
            "length": length
        }

        with open(self.bin_path, "ab") as bf, open(self.jsonl_path, "a") as jf:
            bf.write(raw_bytes)
            jf.write(json.dumps(record) + "\n")

        self.current_inode += 1
        self.current_offset += length
        return self.current_inode

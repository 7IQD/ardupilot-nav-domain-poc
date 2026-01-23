import duckdb
import json
import os

class BridgeAuditor:
    def __init__(self, db_path="bin/nav_domain.db", mapping_path="bin/mapping.json"):
        self.db_path = db_path
        self.mapping_path = mapping_path
        self.summary = {"matches": 0, "mismatches": 0, "missing_tables": 0}

    def run_audit(self, strict=False):
        if not os.path.exists(self.db_path):
            print(f"❌ DATABASE NOT FOUND: {self.db_path}")
            return False

        conn = duckdb.connect(self.db_path)
        with open(self.mapping_path, 'r') as f:
            mapping = json.load(f)

        print(f"\n🕵️  PRE-FLIGHT AUDIT: {os.path.basename(self.db_path)}")
        print("="*50)

        for msg_type, tables in mapping.items():
            for table, fields in tables.items():
                # 1. Fetch live schema
                db_info = [c[1] for c in conn.execute(f"PRAGMA table_info('{table}')").fetchall()]

                if not db_info:
                    print(f"❌ TABLE MISSING: {table}")
                    self.summary["missing_tables"] += 1
                    continue

                print(f"📦 Message: {msg_type} -> Table: {table}")

                # 2. Mandatory Column Check (The Timestamp Guard)
                if "timestamp_us" in db_info:
                    print(f"   ✅ [SYSTEM] timestamp_us detected")
                    self.summary["matches"] += 1
                else:
                    print(f"   ❌ [CRITICAL] timestamp_us MISSING")
                    self.summary["mismatches"] += 1

                # 3. Field Mapping Check
                for mav_key, sql_col in fields.items():
                    if sql_col in db_info:
                        print(f"   ✅ {mav_key.ljust(15)} -> {sql_col}")
                        self.summary["matches"] += 1
                    else:
                        print(f"   ❌ {mav_key.ljust(15)} -> {sql_col} (NOT IN DB)")
                        self.summary["mismatches"] += 1
                print("-" * 30)

        conn.close()
        return self._report(strict)

    def _report(self, strict):
        print("\n📊 AUDIT SUMMARY")
        print(f"   - Valid Matches: {self.summary['matches']}")
        print(f"   - Mismatches:    {self.summary['mismatches']}")
        print(f"   - Missing Tables: {self.summary['missing_tables']}")

        passed = self.summary["mismatches"] == 0 and self.summary["missing_tables"] == 0

        if passed:
            print("\n🟢 STATUS: CLEAR FOR TAKEOFF. Bridge is aligned.")
        else:
            print("\n🔴 STATUS: GROUNDED. Resolve mismatches before flight.")
            if strict:
                raise Exception("Audit Failed: Schema misalignment detected.")
        return passed

if __name__ == "__main__":
    auditor = BridgeAuditor()
    auditor.run_audit(strict=False)
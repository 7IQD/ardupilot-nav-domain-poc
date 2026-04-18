import os
import duckdb

from nav_data_service import NavDataService
from nav_data_integrity_check import NavDataIntegrityCheck
from nav_stats import NavStatsEngine
from nav_labeler import NavLabeler
from nav_verdict_map import NavVerdictMap


class NavController:

    def __init__(self):
        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
        self.db_path = os.path.join(
            BASE_DIR,
            "bin/vault/warehouse_df/NAV_20260319_1332_parts/nav_master.duckdb"
        )

    def _pause(self):
        input("\n[Press ENTER]\n")

    def run(self):

        print("\n🚁 NAV RCA INTERACTIVE\n")

        print(f"📂 Using DB: {self.db_path}\n")   # debug visibility

        con = duckdb.connect(self.db_path, read_only=True)

        # STEP 1
        print("STEP 1: Availability")
        print(NavDataService.check_availability(con))
        self._pause()

        # STEP 2
        print("STEP 2: Integrity")
        print(NavDataIntegrityCheck.check_fields(con))
        self._pause()

        # STEP 3-4
        print("STEP 3–4: Distributions")
        df_status, df_nsats = NavStatsEngine.get_distributions(con)
        print(df_status)
        print(df_nsats)
        self._pause()

        # STEP 5
        print("STEP 5: Mismatch")
        df_mismatch = NavLabeler.get_mismatches(con)
        print(df_mismatch.head(10))
        self._pause()

        # STEP 6
        print("STEP 6: Windows")
        df_windows = NavLabeler.get_windows(con)
        print(df_windows)
        self._pause()

        # STEP 7
        print("STEP 7: Verdict\n")

        verdict = NavVerdictMap.evaluate(df_windows)

        print("🎯 FINAL RCA")
        print(f"Root Cause: {verdict['root_cause']}")
        print(f"Confidence: {verdict['confidence']}\n")

        print("Fixes:")
        for f in verdict["suggested_fixes"]:
            print(f"- {f}")

        print("\n📊 Evidence Table:\n")
        print(f"{'Start':>10} {'End':>12} {'Dur(s)':>8} {'State':>10} {'FC':>10} {'Score':>6} {'Inodes':>20}")
        print("-" * 85)

        for ev in verdict["evidence_table"]:
            print(
                f"{ev['start_time']:>10} "
                f"{ev['end_time']:>12} "
                f"{ev['duration_sec']:>8} "
                f"{ev['sensor_state']:>10} "
                f"{ev['fc_state']:>10} "
                f"{ev['score']:>6} "
                f"{str(ev['start_inode']) + '-' + str(ev['end_inode']):>20}"
            )

        print("\n🔗 Chain Summary:\n")
        for c in verdict["chain_summary"]:
            print(f"→ {c}")

        print("\n🏁 COMPLETE\n")

        con.close()


if __name__ == "__main__":
    NavController().run()
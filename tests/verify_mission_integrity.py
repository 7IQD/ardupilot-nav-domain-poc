import unittest
from src.data_mart_engine.database_manager import DatabaseManager

class TestMissionIntegrity(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseManager()

    def test_nav_no_stacking(self):
        """Verify that Nav Refinery is NOT appending/stacking data."""
        res = self.db.query_gold("SELECT COUNT(*) as count FROM fact_nav_precision")
        # We expect exactly 1665 for MAV_FLIGHT_001
        self.assertEqual(res['count'].iloc[0], 1665, "🚩 Nav data is stacking! Overwrite failed.")

    def test_zero_drop_sys(self):
        """Verify we haven't lost a single packet in the Sys domain."""
        res = self.db.query_gold("SELECT COUNT(*) as count FROM fact_sys_status")
        self.assertEqual(res['count'].iloc[0], 666, "🚩 Sys packets dropped! Zero-drop architecture violated.")

    def test_voltage_accuracy(self):
        """Verify the 12.6V average (Imputation check)."""
        res = self.db.query_gold("SELECT AVG(voltage) as avg_v FROM fact_sys_status")
        self.assertAlmostEqual(res['avg_v'].iloc[0], 12.6, places=1, msg="🚩 Voltage math is polluted!")

if __name__ == "__main__":
    print("🚀 Running Mission Integrity Audit...")
    unittest.main()
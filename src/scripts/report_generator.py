import os
import time
import duckdb
import pandas as pd

class ReportGenerator:
    """
    Generates Engine Health and Cross-Talk Reports from the warehouse.
    """
    def __init__(self, warehouse_dir="bin/vault/warehouse", report_dir="bin/vault/reports"):
        self.warehouse_dir = warehouse_dir
        self.report_dir = report_dir
        os.makedirs(self.report_dir, exist_ok=True)
        # Using a persistent or in-memory DuckDB connection
        self.db = duckdb.connect()

    def _run_health_query(self, master_path):
        """
        DuckDB query to aggregate packet counts and inode ranges.
        """
        return f"""
        SELECT
            src_sys, src_comp, mavpackettype,
            COUNT(*) AS total_pkts,
            MIN(inode) AS start_inode,
            MAX(inode) AS end_inode
        FROM '{master_path}'
        GROUP BY ALL
        """

    def generate_domain_report(self, domain):
        """
        Loads a master parquet file and exports health metrics to a new parquet.
        """
        master_path = os.path.join(self.warehouse_dir, f"{domain}_master.parquet")
        if not os.path.exists(master_path):
            # Domain file doesn't exist; skip without error
            return None

        try:
            df = self.db.query(self._run_health_query(master_path)).to_df()
            # Timestamping the report for versioning
            report_file = os.path.join(self.report_dir, f"{domain}_health_{int(time.time())}.parquet")
            df.to_parquet(report_file, index=False)
            print(f"✅ {domain.upper()} Health Report saved.")
            return report_file
        except Exception as e:
            print(f"❌ Failed to generate {domain.upper()} report: {e}")
            return None

    def generate_all(self):
        """
        Triggers health report generation for all active domains in the POC.
        """
        self.generate_domain_report("nav")
        self.generate_domain_report("est")
        self.generate_domain_report("sys")
        self.generate_domain_report("com")

if __name__ == "__main__":
    # Standard entry point for manual testing
    generator = ReportGenerator()
    generator.generate_all()
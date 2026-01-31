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
        self.db = duckdb.connect()

    def _run_health_query(self, master_path):
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
        master_path = os.path.join(self.warehouse_dir, f"{domain}_master.parquet")
        if not os.path.exists(master_path):
            return None
        
        df = self.db.query(self._run_health_query(master_path)).to_df()
        report_file = os.path.join(self.report_dir, f"{domain}_health_{int(time.time())}.parquet")
        df.to_parquet(report_file, index=False)
        print(f"✅ {domain.upper()} Health Report saved.")
        return report_file

    def generate_all(self):
        self.generate_domain_report("nav")
        self.generate_domain_report("sys")

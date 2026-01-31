import pandas as pd
from src.data_mart_engine.database_manager import DatabaseManager

class UniversalSummaryEngine:
    def __init__(self):
        self.db = DatabaseManager()

    def run_discovery(self):
        table_query = "SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'fact_%'"
        tables_df = self.db.query_gold(table_query)

        if tables_df is None or tables_df.empty:
            print("📭 No fact tables found in the Gold Vault.")
            return

        print("\n" + "════" * 15)
        print(" 🛰️  UNIVERSAL DATA MART SUMMARY (ALL DOMAINS) ")
        print("════" * 15)

        for table in tables_df['table_name']:
            self.summarize_table(table)

        print("════" * 15 + "\n")

    def summarize_table(self, table_name):
        domain = table_name.replace('fact_', '').upper()

        # 1. Get column metadata
        col_query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'"
        cols = self.db.query_gold(col_query)
        col_list = cols['column_name'].tolist()

        # 2. Identify unique missions
        mission_query = f"SELECT DISTINCT mission_id FROM {table_name}"
        mission_list = self.db.query_gold(mission_query)['mission_id'].tolist()
        missions_str = ", ".join(mission_list) if mission_list else "NONE"

        # 3. Handle Data Health (Raw vs Imputed)
        health_str = "100% Raw / 0% Imputed" # Default
        if 'is_imputed' in col_list:
            health_query = f"SELECT COUNT(*) as total, SUM(is_imputed) as imp FROM {table_name}"
            h_res = self.db.query_gold(health_query).iloc[0]
            total = h_res['total']
            imp = h_res['imp'] or 0
            raw_pct = ((total - imp) / total) * 100
            imp_pct = (imp / total) * 100
            health_str = f"{raw_pct:.0f}% Raw / {imp_pct:.0f}% Imputed"

        # 4. Identify numeric columns for averages (Excluding flags)
        numeric_cols = cols[cols['data_type'].str.contains('DOUBLE|FLOAT|INT|DECIMAL', case=False, na=False)]
        metrics = [c for c in numeric_cols['column_name'] if c not in ['mission_id', 'id', 'ekf_healthy', 'is_imputed']]

        # 5. Build dynamic SQL for stats
        agg_funcs = ["COUNT(*) as total_rows", "MIN(timestamp) as start_t", "MAX(timestamp) as end_t"]
        for m in metrics:
            agg_funcs.append(f"AVG({m}) as avg_{m}")
            agg_funcs.append(f"MAX({m}) as max_{m}")

        summary_query = f"SELECT {', '.join(agg_funcs)} FROM {table_name}"
        res = self.db.query_gold(summary_query).iloc[0]

        print(f"\n 🔹 DOMAIN: {domain}")
        print(f"   • Missions:    {missions_str}")
        print(f"   • Data Points: {int(res['total_rows'])}")
        print(f"   • Data Health: {health_str}")
        print(f"   • Time Span:   {res['start_t']} ⮕ {res['end_t']}")

        if metrics:
            print("   • Key Metrics (Averages):")
            for m in metrics:
                label = m.replace('_', ' ').title()
                print(f"     - {label}: {res[f'avg_{m}']:.4f} (Peak: {res[f'max_{m}']:.4f})")

if __name__ == "__main__":
    UniversalSummaryEngine().run_discovery()
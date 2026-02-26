import pandas as pd
from data_mart_engine.database_manager import DatabaseManager

class UniversalSummaryEngine:
    """
    Generates a cross-domain summary of all 'fact_' tables in Gold Vault.
    Includes table existence checks and dynamic data health analysis.
    """
    def __init__(self):
        self.db = DatabaseManager()

    def run_discovery(self):
        # Step 0: Check if any Gold tables exist
        table_query = "SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'fact_%'"
        tables_df = self.db.query_gold(table_query)

        if tables_df is None or tables_df.empty:
            print(f"⚠️ No fact tables found in Gold Vault at: {self.db.db_path}")
            return

        tables = tables_df['table_name'].tolist()

        print("\n" + "════" * 15)
        print(" 🛰️  UNIVERSAL DATA MART SUMMARY (ALL DOMAINS) ")
        print(f" 📂 Path: {self.db.db_path}")
        print("════" * 15)

        for table in tables:
            self.summarize_table(table)

        print("════" * 15 + "\n")

    def summarize_table(self, table_name):
        domain = table_name.replace('fact_', '').upper()

        # Step 1: Column metadata
        col_query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'"
        cols = self.db.query_gold(col_query)
        if cols.empty: return

        col_list = cols['column_name'].tolist()

        # Step 2: Missions
        mission_query = f"SELECT DISTINCT mission_id FROM {table_name}"
        mission_list_df = self.db.query_gold(mission_query)
        missions_str = ", ".join(mission_list_df['mission_id'].astype(str).tolist()) if not mission_list_df.empty else "NONE"

        # Step 3: Data Health
        health_str = "100% Raw / 0% Imputed"
        if 'is_imputed' in col_list:
            health_query = f"SELECT COUNT(*) as total, SUM(CAST(is_imputed AS INT)) as imp FROM {table_name}"
            h_res_df = self.db.query_gold(health_query)
            if not h_res_df.empty:
                h_res = h_res_df.iloc[0]
                total = h_res['total']
                imp = h_res['imp'] if h_res['imp'] is not None else 0
                if total > 0:
                    raw_pct = ((total - imp) / total) * 100
                    imp_pct = (imp / total) * 100
                    health_str = f"{raw_pct:.0f}% Raw / {imp_pct:.0f}% Imputed"

        # Step 4: Identify numeric columns for summary
        # 🔹 FIX: Explicitly exclude 'timestamp' from metrics list to prevent <NA>
        numeric_cols = cols[cols['data_type'].str.contains('DOUBLE|FLOAT|INT|DECIMAL|HUGEINT', case=False, na=False)]
        excluded = ['mission_id', 'id', 'ekf_healthy', 'is_imputed', 'domain', 'timestamp']
        metrics = [c for c in numeric_cols['column_name'] if c.lower() not in excluded]

        # Step 5: Build dynamic SQL for stats
        # Timestamp is used for MIN/MAX only
        agg_funcs = ["COUNT(*) as total_rows", "MIN(timestamp) as start_t", "MAX(timestamp) as end_t"]
        for m in metrics:
            agg_funcs.append(f"AVG({m}) as avg_{m}")
            agg_funcs.append(f"MAX({m}) as max_{m}")

        try:
            summary_query = f"SELECT {', '.join(agg_funcs)} FROM {table_name}"
            res_df = self.db.query_gold(summary_query)
            if res_df.empty: return
            res = res_df.iloc[0]

            # Step 6: Display
            print(f"\n 🔹 DOMAIN: {domain}")
            print(f"   • Missions:    {missions_str}")
            print(f"   • Data Points: {int(res['total_rows'])}")
            print(f"   • Data Health: {health_str}")
            print(f"   • Time Span:   {res['start_t']} ⮕ {res['end_t']}")

            if metrics:
                print("   • Key Metrics (Averages):")
                for m in metrics:
                    label = m.replace('_', ' ').title()
                    # Safe display for NaN results
                    val = res[f'avg_{m}'] if not pd.isna(res[f'avg_{m}']) else 0.0
                    peak = res[f'max_{m}'] if not pd.isna(res[f'max_{m}']) else 0.0
                    print(f"     - {label}: {val:.4f} (Peak: {peak:.4f})")

        except Exception as e:
            print(f"❌ Summary Error for {table_name}: {e}")

if __name__ == "__main__":
    UniversalSummaryEngine().run_discovery()
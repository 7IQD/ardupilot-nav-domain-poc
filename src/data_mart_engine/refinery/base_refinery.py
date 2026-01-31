import os
import pandas as pd
import logging

class BaseRefinery:
    def __init__(self):
        self.warehouse_path = "bin/vault/warehouse"
        self.gold_path = "bin/vault/gold"
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)

    def load_from_warehouse(self, parquet_file: str) -> pd.DataFrame:
        """Reads a master file from the warehouse zone."""
        path = os.path.join(self.warehouse_path, parquet_file)
        if not os.path.exists(path):
            self.logger.warning(f"⚠️ Warehouse file not found: {path}")
            return pd.DataFrame()

        self.logger.info(f"📂 Loading warehouse data: {path}")
        return pd.read_parquet(path)

    def export_to_gold_parquet(self, df: pd.DataFrame, domain: str, mission_id: str):
        """Saves the refined facts to the Gold Parquet structure."""
        out_dir = os.path.join(self.gold_path, domain, str(mission_id))
        os.makedirs(out_dir, exist_ok=True)

        file_name = f"fact_{domain}_precision.parquet" if domain == "nav" else f"fact_{domain}_status.parquet"
        out_path = os.path.join(out_dir, file_name)

        df.to_parquet(out_path, index=False)
        self.logger.info(f"✨ Gold Parquet minted: {out_path}")
        return out_path

    def get_latest_mission_id(self, df: pd.DataFrame) -> str:
        """Helper to extract mission ID from telemetry."""
        if 'mission_id' in df.columns and not df.empty:
            return str(df['mission_id'].iloc[-1])
        return "UNKNOWN_MISSION"
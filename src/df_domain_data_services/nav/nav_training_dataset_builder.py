import os
import pandas as pd

from src.df_domain_data_services.nav.nav_labeler import NavLabeler, detect_phase


class NavTrainingDatasetBuilder:
    """
    Converts NAV telemetry + labels into ML-ready dataset
    """

    def __init__(self, mission_id: str, df: pd.DataFrame):
        self.mission_id = mission_id
        self.df = df.copy()

    def build(self):

        # -------------------------
        # Phase detection
        # -------------------------
        df = detect_phase(self.df)

        # -------------------------
        # Apply NAV labeling
        # -------------------------
        labeler = NavLabeler(self.mission_id, df)
        events = labeler.get_mission_scorecard(mode="forensic")

        # -------------------------
        # Feature engineering
        # -------------------------
        df["speed_mag"] = (df["VN"]**2 + df["VE"]**2 + df["VD"]**2) ** 0.5

        df["roll_rate"] = df["Roll"].diff()
        df["pitch_rate"] = df["Pitch"].diff()
        df["yaw_rate"] = df["Yaw"].diff()

        df["alt_rate"] = df["Alt"].diff()

        # -------------------------
        # Attach event labels
        # -------------------------
        df["label"] = "HEALTHY"

        for _, event in events.iterrows():

            mask = (
                (df["TimeUS"] >= event["start_t"]) &
                (df["TimeUS"] <= event["end_t"])
            )

            df.loc[mask, "label"] = event["label"]

        # -------------------------
        # ML feature selection
        # -------------------------
        features = [
            "TimeUS",
            "Lat",
            "Lng",
            "Alt",
            "speed_mag",
            "roll_rate",
            "pitch_rate",
            "yaw_rate",
            "alt_rate",
            "NSats",
            "HDop",
            "phase",
            "label"
        ]

        df_ml = df[features].dropna().reset_index(drop=True)

        return df_ml


    def save(self, output_path):

        df_ml = self.build()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        df_ml.to_parquet(output_path)

        print("✅ Training dataset saved:", output_path)
        print("Rows:", len(df_ml))
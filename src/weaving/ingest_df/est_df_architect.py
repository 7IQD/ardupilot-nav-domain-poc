from weaving.ingest_df.df_mavlink_architect import DFIngressMavArchitect

class EstDFArchitect(DFIngressMavArchitect):
    def __init__(self, bin_path, limit=5000):
        super().__init__(
            bin_path=bin_path,
            domain_key="EST",
            msg_types=["ATT", "XKF1", "NKF1", "AHR2"],
            limit=limit
        )
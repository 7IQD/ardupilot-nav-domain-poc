from weaving.ingest_df.df_mavlink_architect import DFIngressMavArchitect

class ComDFArchitect(DFIngressMavArchitect):
    def __init__(self, bin_path, limit=5000):
        super().__init__(
            bin_path=bin_path,
            domain_key="COM",
            msg_types=["RSSI", "Chan", "Val"],
            limit=limit
        )
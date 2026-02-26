from weaving.ingest_df.df_mavlink_architect import DFIngressMavArchitect

class PowerDFArchitect(DFIngressMavArchitect):
    def __init__(self, bin_path, limit=5000):
        super().__init__(
            bin_path=bin_path,
            domain_key="POWER",
            msg_types=["Volt", "Curr", "Enrg", "Temp"],
            limit=limit
        )
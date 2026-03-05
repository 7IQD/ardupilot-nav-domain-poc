import uuid
import duckdb

class NavLabeler:
    def __init__(self, mission_id, db_path):
        self.mission_id = mission_id
        self.db_path = db_path
        # Late import to avoid circular dependency
        from .nav_data_service import NavDataService
        self.data_service = NavDataService(mission_id, db_path)

    def execute_pipeline(self):
        df = self.data_service.fetch_fused_telemetry()
        if df.empty: return 0

        windows = self._generate_windows(df)

        with duckdb.connect(self.db_path) as con:
            self._commit_to_vault(windows, con)
        return len(windows)

    def _generate_windows(self, df):
        windows = []
        active = {"NO_FIX": None, "HIGH_HDOP": None}

        for row in df.itertuples():
            ts = int(row.TimeUS)

            # Rule: NO_FIX
            is_no_fix = (row.HDop == 0 or row.NSats < 6)
            self._stitch(ts, is_no_fix, "NO_FIX", "ENVIRONMENT", active, windows)

            # Rule: HIGH_HDOP
            is_high_hdop = (row.HDop > 2.0 and not is_no_fix)
            self._stitch(ts, is_high_hdop, "HIGH_HDOP", "ENVIRONMENT", active, windows)

        return windows

    def _stitch(self, ts, condition, label, attr, active, windows):
        if condition and not active[label]:
            active[label] = ts
        elif not condition and active[label]:
            windows.append({
                "mission_id": self.mission_id,
                "window_id": f"NAV_{label}_{uuid.uuid4().hex[:4]}",
                "label": label,
                "start_time": active[label],
                "end_time": ts,
                "attribution": attr
            })
            active[label] = None

    def _commit_to_vault(self, windows, con):
        con.execute("CREATE TABLE IF NOT EXISTS fact_nav_labels (mission_id TEXT, window_id TEXT, label TEXT, start_time BIGINT, end_time BIGINT, attribution TEXT)")
        con.execute("DELETE FROM fact_nav_labels WHERE mission_id = ?", [self.mission_id])
        if windows:
            for w in windows:
                con.execute("INSERT INTO fact_nav_labels VALUES (?, ?, ?, ?, ?, ?)", list(w.values()))
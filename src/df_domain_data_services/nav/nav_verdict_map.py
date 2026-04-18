class NavVerdictMap:
    """
    STEP 7: Deterministic RCA Verdict
    - Uses ONLY anomaly (MISMATCH) windows
    - Confidence = time-weighted evidence quality
    """

    @staticmethod
    def evaluate(df_windows):

        # -------------------------------
        # No data case
        # -------------------------------
        if df_windows.empty:
            return {
                "root_cause": "No Data",
                "confidence": "0.0 (LOW)",
                "suggested_fixes": [],
                "evidence_table": []
            }

        # -------------------------------
        # Filter ONLY anomaly windows
        # -------------------------------
        anomaly_windows = df_windows[
            df_windows["integrity_flag"] == "MISMATCH"
        ]

        if anomaly_windows.empty:
            return {
                "root_cause": "Nominal Flight",
                "confidence": "0.99 (HIGH)",
                "suggested_fixes": ["None required"],
                "evidence_table": []
            }

        # -------------------------------
        # Build Evidence Table
        # -------------------------------
        evidence_table = []

        for _, row in anomaly_windows.iterrows():

            # Stage evaluation (pattern logic)
            s1 = row["sensor_state"] == "LOSS"
            s2 = row["fc_state"] == "HEALTHY"
            s3 = row["integrity_flag"] == "MISMATCH"

            # Weighted scoring (quality of evidence)
            score = (
                (0.3 if s1 else 0) +
                (0.3 if s2 else 0) +
                (0.4 if s3 else 0)
            )

            evidence_table.append({
                "start_time": row["start_time"],
                "end_time": row["end_time"],
                "duration_sec": row["duration_sec"],
                "start_inode": row["start_inode"],
                "end_inode": row["end_inode"],
                "sensor_state": row["sensor_state"],
                "fc_state": row["fc_state"],
                "flag": row["integrity_flag"],
                "score": round(score, 2)
            })

        # -------------------------------
        # Time-weighted Confidence
        # -------------------------------
        weighted_score = sum(
            ev["score"] * ev["duration_sec"] for ev in evidence_table
        )

        total_duration = sum(
            ev["duration_sec"] for ev in evidence_table
        )

        avg_score = weighted_score / total_duration if total_duration > 0 else 0

        # -------------------------------
        # Confidence Label
        # -------------------------------
        if avg_score > 0.8:
            label = "HIGH"
        elif avg_score > 0.5:
            label = "MEDIUM"
        else:
            label = "LOW"

        # -------------------------------
        # Final Verdict
        # -------------------------------
        return {
        "root_cause": "GPS Loss with EKF Lag (Hysteresis Gap)",
        "confidence": f"{round(avg_score, 2)} ({label})",
        "suggested_fixes": [
            "Check GPS signal obstruction (trees/buildings)",
            "Verify RF interference (VTX/telemetry)",
            "Inspect GPS antenna and wiring",
            "Review EKF thresholds (FS_EKF_THRESH)"
        ],
        "evidence_table": evidence_table,
        "chain_summary": [
            f"{ev['sensor_state']}->{ev['fc_state']} ({ev['duration_sec']}s)"
            for ev in evidence_table
        ]
    }
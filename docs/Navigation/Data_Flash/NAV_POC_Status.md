## NAV Domain Status

1. To support NAV domain analysis, a set of NAV-related test scripts have been created to generate controlled anomalies in SITL. These anomalies simulate realistic flight failures such as GPS glitch, high vibration, IMU clipping, compass interference, radio signal loss and EKF divergence. The purpose of these scripts is to generate .BIN files.

2. List of scripts to generate the BIN files in the ~/tests/ folder:

```bash
gps_test_GPS_EKF_GLITCH.py   # Tests EKF response to GPS glitches
gps_test_com_failure.py      # Verifies impact of COM link failures on GPS telemetry
gps_test_gps_loss.py         # Handles GPS signal loss scenarios
gps_test_imu_failure.py      # Monitors GPS/EKF interaction under IMU noise
gps_test_vibration.py        # Observes GPS performance under high vibration

3. These scripts generated the following .BIN files in bin/vault/df_source/ for validation and analysis during SITL runs:
   T1_GPS_LOSS_RUN01.BIN          # GPS glitch
   T2_VIBRATION_RUN01.BIN         # Vibration spike
   T3_IMU_FAIL_RUN01.BIN          # IMU clipping / high-noise stress
   T4_COMPASS_FAIL.BIN            # Compass interference
   T5_COM_LINK_FAIL.BIN / T5_COM_FAIL_RUN02.BIN  # Radio (COM) loss
   T6_GPS_GLITCH_EKF.BIN          # EKF / GPS glitch interaction

4. Now, the module needs to detect each failure, assign a specific label, and present the results so developers can perform causal analysisL
   Labels:
      normal
      vibration_fault
      gps_failure
      imu_clipping
      ekf_instability
   Labeled event table:
      mission_id
      start_time
      end_time
      phase
      label
      severity

5. These labeled events form the training dataset, stored as nav_training_dataset.parquet for Feature Extraction. The module extracts relevant features for analysis through the labeled NAV signals.
   Features include:
      vibration magnitude
      IMU noise
      EKF velocity stability
      GPS quality
      battery voltage drops
      radio RSSI
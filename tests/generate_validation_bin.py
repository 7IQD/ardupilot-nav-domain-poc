import os
import numpy as np
from pymavlink.dfactor import DFWriter

TARGET_PATH = "../../bin/vault/df_source/controlled_validation.bin"

def generate_bin():
    os.makedirs(os.path.dirname(TARGET_PATH), exist_ok=True)

    log = DFWriter(TARGET_PATH)

    TOTAL_US = 10_000_000      # 10 seconds
    STEP_US  = 20_000          # 50Hz loop

    for t_us in range(0, TOTAL_US + STEP_US, STEP_US):

        # ---- DUPLICATE TEST (exact same TimeUS at 2s) ----
        reps = 2 if t_us == 2_000_000 else 1

        for r in range(reps):

            # ---- EST DOMAIN (50Hz) ----
            # Silence between 4.5s and 4.6s
            if not (4_500_000 <= t_us <= 4_600_000):
                roll = 99.0 if t_us in [2_000_000, 4_000_000, 6_000_000, 8_000_000] else 10.0
                log.write('ATT', TimeUS=t_us, Roll=roll, Pitch=5.0, Yaw=180.0)

            # ---- NAV DOMAIN (10Hz) ----
            if t_us % 100_000 == 0:
                lat = np.nan if t_us == 5_000_000 else 45.0
                log.write('GPS', TimeUS=t_us, Lat=lat, Lng=-75.0, Alt=100.0, Spd=15.0)

            # ---- COM DOMAIN (5Hz) ----
            # Dropout after 8s
            if t_us % 200_000 == 0 and t_us < 8_000_000:
                log.write('RAD', TimeUS=t_us, RSSI=180, RemRSS=170)

            # ---- POWER DOMAIN (2Hz) ----
            if t_us % 500_000 == 0:
                # Drift 5ms at exactly 4s
                ts = t_us + 5_000 if t_us == 4_000_000 else t_us
                log.write('BAT', TimeUS=ts, Volt=24.0, CurrTot=10.0, EnrgTot=500.0)

            # ---- SYS DOMAIN (1Hz) ----
            if t_us % 1_000_000 == 0:
                log.write('PM', TimeUS=t_us, Load=25, Mem=512000)

    log.close()
    print(f"✅ Created: {TARGET_PATH}")

if __name__ == "__main__":
    generate_bin()
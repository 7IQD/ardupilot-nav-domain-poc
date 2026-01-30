# SCHEMA_CONTRACTS: The formal agreement between Refinery and Dashboard
SCHEMA_CONTRACTS = {
    # The 'Cola': Just the final error for flight safety
    "pilot": ["timestamp", "mag_err"],

    # The 'Beer': All 4 slices for the EKF Expert
    "ekf": ["timestamp", "lat_err", "lon_err", "mag_err"],

    # The 'Whiskey': Everything for forensic reconstruction
    "forensics": None
}
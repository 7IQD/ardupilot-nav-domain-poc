#!/usr/bin/env python3
"""
df_action_map.py
The Authority on Domain Schemas.
Maps raw ArduPilot DataFlash message fields to standardized Warehouse tables.

Architecture Contract:
• Architects discover fields from MAVLink/DataFlash logs.
• The Refiner ONLY materializes columns authorized here.
• This guarantees deterministic schemas and zero data leakage.
"""

class DFActionMap:
    """
    Canonical schema authority for the DataFlash warehouse.
    """

    # -------------------------------------------------------
    # Message Routing
    # Which DataFlash messages belong to each domain
    # -------------------------------------------------------
    MSG_MAP = {
        # Navigation domain
        "NAV": [
            "ATT",
            "POS",
            "GPS",
            "AHR2",
            "XKF1"
        ],

        # Estimator / sensor fusion domain
        "EST": [
            "NKF1",
            "VIBE",
            "IMU"
        ],

        # System health domain
        "SYS": [
            "PM",
            "MCU",
            "POWR"
        ],

        # Electrical / battery telemetry
        "POWER": [
            "BAT"
        ],

        # Communications / RC link
        "COM": [
            "RADIO",
            "RCIN",
            "RCOUT"
        ]
    }

    # -------------------------------------------------------
    # Canonical Domain Schemas
    # (Exact DataFlash field names)
    # -------------------------------------------------------
    DOMAINS = {
        # Navigation / flight path
        "NAV": [
            "TimeUS",
            "Lat",
            "Lng",
            "Alt",
            "Spd",
            "NSats",
            "HDop",
            "Status",
            "Roll",
            "Pitch",
            "Yaw"
        ],

        # Estimator + IMU + vibration telemetry
        "EST": [
            "TimeUS",
            # attitude
            "Roll",
            "Pitch",
            "Yaw",
            # velocity estimates
            "VN",
            "VE",
            "VD",
            # vibration telemetry (VIBE message)
            "VibeX",
            "VibeY",
            "VibeZ",
            "Clip",
            # IMU telemetry (IMU message)
            "GyrX",
            "GyrY",
            "GyrZ",
            "AccX",
            "AccY",
            "AccZ"
        ],

        # Autopilot system health
        "SYS": [
            "TimeUS",
            "Load",
            "Mem",
            "KHz"
        ],

        # Power system
        "POWER": [
            "TimeUS",
            "Volt",
            "Amp",
            "EnrgTot",
            "Temp"
        ],

        # Telemetry / RC link
        "COM": [
            "TimeUS",
            "RSSI",
            "RemRSS",
            "TxPwr"
        ]
    }

    # -------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------

    @staticmethod
    def get_msg_types(domain: str):
        """Return MAVLink/DataFlash message types for a domain."""
        if not domain:
            return []
        return DFActionMap.MSG_MAP.get(domain.upper(), [])

    @staticmethod
    def get_columns(domain: str):
        """Return canonical warehouse columns for a domain."""
        if not domain:
            return []
        return DFActionMap.DOMAINS.get(domain.upper(), [])

    @staticmethod
    def get_domains():
        """
        Return all domains.
        MISC is included as a fallback safety domain.
        """
        domains = list(DFActionMap.DOMAINS.keys())
        if "MISC" not in domains:
            domains.append("MISC")
        return domains
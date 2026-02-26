class DFActionMap:
    """
    The Authority on Domain Schemas.
    Maps raw ArduPilot message fields to standardized Warehouse columns.
    """

    # 1. Define which raw messages belong to which domain.
    # Used by df_main.py to know what to extract from the .BIN file.
    MSG_MAP = {
        'NAV':   ['ATT', 'POS', 'GPS', 'AHR2'],
        'EST':   ['XKF1', 'NKF1', 'VIBE'],
        'SYS':   ['POWR', 'MCU', 'PM'],
        'POWER': ['BAT', 'POWR'],
        'COM':   ['RADIO', 'RCIN']
    }

    # 2. Define the final schema for the Warehouse (Vault C).
    # 'NSats' is now correctly added to the NAV domain.
    DOMAINS = {
        'NAV':   ['TimeUS', 'Roll', 'Pitch', 'Yaw', 'Lat', 'Lng', 'Alt', 'Spd', 'NSats'],
        'EST':   ['TimeUS', 'Roll', 'Pitch', 'Yaw', 'Lat', 'Lng', 'Alt'],
        'SYS':   ['TimeUS', 'Load', 'NLoad', 'Mem'],
        'POWER': ['TimeUS', 'Volt', 'Amp', 'Volt_R', 'CurrTot'],
        'COM':   ['TimeUS', 'RSSI', 'RemRSS', 'TxPwr']
    }

    # 3. Rename Logic (Source -> Target).
    SOURCE_MAPPING = {
        'POWER': {
            'Amp': 'Curr',
            'Volt_R': 'VoltR'
        },
        'SYS': {
            'Load': 'Load'
        }
    }

    @staticmethod
    def get_msg_types(domain):
        """Returns ArduPilot message types for the ingress stage."""
        return DFActionMap.MSG_MAP.get(domain.upper(), [])

    @staticmethod
    def get_columns(domain):
        """Returns the final column list for the refining stage."""
        return DFActionMap.DOMAINS.get(domain.upper(), [])

    @staticmethod
    def get_domains():
        """Returns all registered domains (matching what df_refinery.py expects)."""
        return list(DFActionMap.DOMAINS.keys())
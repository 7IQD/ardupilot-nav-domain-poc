class DFActionMap:
    """
    The Authority on Domain Schemas.
    Maps raw ArduPilot message fields to standardized Warehouse tables.
    """
    # MSG_MAP: Which MAVLink messages belong to which domain
    MSG_MAP = {
        'NAV':   ['ATT', 'POS', 'GPS', 'AHR2', 'XKF1'],
        'EST':   ['NKF1', 'VIBE', 'IMU'],
        'SYS':   ['PM', 'MCU', 'POWR'],
        'POWER': ['BAT'],
        'COM':   ['RADIO', 'RCIN', 'RCOUT']
    }

    # DOMAINS: The canonical hardware columns (exact FMT names)
    DOMAINS = {
        'NAV':   ['TimeUS', 'Lat', 'Lng', 'Alt', 'Spd', 'NSats', 'HDop', 'Status', 'Roll', 'Pitch', 'Yaw'],
        'EST':   ['TimeUS', 'Roll', 'Pitch', 'Yaw', 'VN', 'VE', 'VD'],
        'SYS':   ['TimeUS', 'Load', 'Mem', 'KHz'],
        'POWER': ['TimeUS', 'Volt', 'Amp', 'EnrgTot', 'Temp'],
        'COM':   ['TimeUS', 'RSSI', 'RemRSS', 'TxPwr']
    }

    @staticmethod
    def get_msg_types(domain):
        return DFActionMap.MSG_MAP.get(domain.upper(), [])

    @staticmethod
    def get_columns(domain):
        return DFActionMap.DOMAINS.get(domain.upper(), [])

    @staticmethod
    def get_domains():
        # Includes MISC by default as the safety net
        return list(DFActionMap.DOMAINS.keys()) + ['MISC']
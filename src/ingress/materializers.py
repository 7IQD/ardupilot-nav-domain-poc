# src/ingress/materializers.py
import logging

# Logger setup
logger = logging.getLogger("MATERIALIZER")
logger.setLevel(logging.INFO)
if not logger.handlers:
    import sys
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[%(asctime)s] %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Field mapping JSON
FIELD_MAP = {
    "SYS_STATUS": {
        "sys_battery": {
            "voltage_battery": "volt_raw",
            "current_battery": "curr_raw",
            "battery_remaining": "battery_remaining"
        }
    },
    "GLOBAL_POSITION_INT": {
        "nav_gps": {
            "lat": "lat",
            "lon": "lon",
            "alt": "alt",
            "relative_alt": "rel_alt",
            "vx": "vx",
            "vy": "vy",
            "vz": "vz"
        }
    },
    "ATTITUDE": {
        "nav_attitude": {
            "roll": "roll",
            "pitch": "pitch",
            "yaw": "yaw",
            "rollspeed": "roll_speed",
            "pitchspeed": "pitch_speed",
            "yawspeed": "yaw_speed"
        }
    }
}

# -----------------------------
# Generic Dynamic Materializer
# -----------------------------
def decode_message(msg_bytes):
    """
    Dynamically converts a MAVLink msg_bytes dict into a Python object per domain.
    """
    try:
        msgid = msg_bytes.get("msgid")
        if msgid not in FIELD_MAP:
            logger.warning(f"Unknown msgid '{msgid}' encountered")
            return None

        domain_name, field_map = list(FIELD_MAP[msgid].items())[0]

        class Msg:
            pass

        obj = Msg()
        for out_field, raw_field in field_map.items():
            setattr(obj, out_field, msg_bytes.get(raw_field, 0))

        return obj
    except Exception as e:
        logger.error(f"decode_message failed for {msg_bytes.get('msgid')}: {e}")
        return None

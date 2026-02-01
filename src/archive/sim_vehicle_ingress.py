# src/ingress/sim_vehicle_ingress.py
import logging
import threading
import time
from src.ingress.architect import NavArchitect
# from src.ingress.sys_architect import SysArchitect  # Uncomment when SysArchitect implemented
# from pymavlink import mavutil  # Uncomment for real UDP/MAVLink input

# -------------------------------
# Configure Logging
# -------------------------------
logging.basicConfig(
    filename='logs/dispatcher.log',
    level=logging.INFO,
    format='[%(asctime)s] %(name)-12s %(levelname)-8s %(message)s'
)
logger = logging.getLogger("DISPATCHER")

# -------------------------------
# Domain ID Mappings (example)
# -------------------------------
NAV_IDS = {24, 33, 33}      # e.g., GLOBAL_POSITION_INT, GPS_RAW_INT, etc.
SYS_IDS = {1, 2, 3}         # e.g., SYS_STATUS, POWER_STATUS, etc.

# -------------------------------
# Instantiate Architects
# -------------------------------
nav_architect = NavArchitect()
# sys_architect = SysArchitect()  # Uncomment when implemented

# -------------------------------
# Dispatcher Logic
# -------------------------------
def dispatch_packet(msg):
    """Forward the MAVLink message to the correct Architect."""
    try:
        if msg.msgid in NAV_IDS:
            nav_architect.ingest(msg)
            logger.info(f"Dispatched NAV packet: time_boot_ms={getattr(msg, 'time_boot_ms', 'N/A')}")
        elif msg.msgid in SYS_IDS:
            # sys_architect.ingest(msg)
            logger.info(f"Dispatched SYS packet: time_boot_ms={getattr(msg, 'time_boot_ms', 'N/A')}")
        else:
            logger.debug(f"Ignored packet msgid={msg.msgid}")
    except Exception as e:
        logger.error(f"Dispatch Error for msgid={msg.msgid}: {e}")

# -------------------------------
# Simulated Ingress Loop (UDP / MAVLink)
# -------------------------------
def ingress_loop(stop_event, msg_generator):
    """Simulated packet ingestion loop."""
    logger.info("Ingress loop started.")
    while not stop_event.is_set():
        try:
            msg = next(msg_generator)
            dispatch_packet(msg)
            # Minimal sleep to simulate high-frequency traffic
            time.sleep(0.001)
        except StopIteration:
            logger.info("Message generator exhausted. Ending ingress loop.")
            break
        except Exception as e:
            logger.error(f"Ingress loop error: {e}")

    # Ensure final flush
    nav_architect.stop()
    # sys_architect.stop()  # Uncomment when implemented
    logger.info("Ingress loop finished. Architects flushed final segments.")

# -------------------------------
# Example Msg Generator
# -------------------------------
def example_msg_generator(total=1000):
    """Simulated MAVLink messages for testing."""
    for i in range(total):
        class Msg:
            msgid = 24  # Example NAV message
            time_boot_ms = 158787099 + i
            lat = -353632620 + i
            lon = 1491652373 + i
            alt = 604070 + i
            relative_alt = 50000 + i
            vx, vy, vz = 100 + i, -50 + i, 10 + i
        yield Msg()

# -------------------------------
# Run Simulation
# -------------------------------
if __name__ == "__main__":
    stop_event = threading.Event()
    t = threading.Thread(target=ingress_loop, args=(stop_event, example_msg_generator()))
    t.start()
    t.join()
    logger.info("🏁 sim_vehicle_ingress simulation complete.")

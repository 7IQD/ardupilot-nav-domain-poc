import threading
import logging
import os
import time
from src.ingress.nav_architect import NavArchitect
from src.ingress.nav_clerk import NavClerk
from src.ingress.sys_architect import SysArchitect
from src.ingress.sys_clerk import SysClerk

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/vault_activity.log',
    level=logging.INFO,
    format='[%(asctime)s] %(name)-10s %(levelname)-8s %(message)s'
)

stop_event = threading.Event()

def nav_worker():
    architect = NavArchitect()
    clerk = NavClerk()
    # Example simulation
    for i in range(500):
        class Msg:
            time_boot_ms = 158787099 + i
            lat, lon, alt = -353632620 + i, 1491652373 + i, 604070 + i
            relative_alt, vx, vy, vz = 50000 + i, 100 + i, -50 + i, 10 + i
        architect.ingest(Msg())
        time.sleep(0.01)
    architect.stop()
    logging.info("Nav Architect Finished")
    clerk.maintenance_loop(stop_event=None, single_pass=True)
    logging.info("Nav Clerk Final Flush Done")

def sys_worker():
    architect = SysArchitect()
    clerk = SysClerk()
    # Example simulation
    for i in range(500):
        class Msg:
            time_boot_ms = 158787099 + i
            voltage, current, remaining = 12600, 2811, 95
        architect.ingest(Msg())
        time.sleep(0.01)
    architect.stop()
    logging.info("Sys Architect Finished")
    clerk.maintenance_loop(stop_event=None, single_pass=True)
    logging.info("Sys Clerk Final Flush Done")

if __name__ == "__main__":
    t_nav = threading.Thread(target=nav_worker)
    t_sys = threading.Thread(target=sys_worker)
    t_nav.start()
    t_sys.start()
    t_nav.join()
    t_sys.join()
    print("🏁 Multi-domain Flight Test Simulation Completed")

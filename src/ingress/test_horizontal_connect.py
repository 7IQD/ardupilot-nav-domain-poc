import os
import time
import logging
import duckdb
from ingress.data_manager import DataManager
from ingress.ingress_switch import IngressSwitch
from ingress.nav_decoder_clerk import NavDecoder
from ingress.sys_decoder_clerk import SysDecoder
from ingress.materializers import NavMaterializer, SysMaterializer

# ----------------------------
# Logging Setup
# ----------------------------
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/horizontal_connect.log",
    level=logging.INFO,
    format='[%(asctime)s] %(name)-12s %(levelname)-8s %(message)s'
)
logger = logging.getLogger("HORIZONTAL_TEST")

# ----------------------------
# Mock MAVLink Message
# ----------------------------
class MockMsg:
    def __init__(self, m_type, **kwargs):
        self._type = m_type
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_type(self):
        return self._type

# ----------------------------
# Horizontal Connect Test
# ----------------------------
def test_horizontal_connect():
    DB_PATH = "bin/nav_domain.db"
    LOG_DIR = "ingress/bin"

    logger.info("Initializing DataManager and Materializers...")
    dm = DataManager(LOG_DIR, DB_PATH)
    nav_mat = NavMaterializer(DB_PATH)
    sys_mat = SysMaterializer(DB_PATH)

    switch = IngressSwitch(
        nav_decoder=NavDecoder(nav_mat),
        sys_decoder=SysDecoder(sys_mat)
    )

    # ------------------------
    # Atomic Identity Gate
    # ------------------------
    test_wall_ns = time.time_ns()
    inode, _ = dm.write_bronze_with_anchor(b"HORIZONTAL_TEST_DATA", test_wall_ns)
    logger.info(f"Dispatching Inode {inode} at wall_ns {test_wall_ns}")

    # ------------------------
    # Simulate Horizontal Burst
    # ------------------------
    gps_msg = MockMsg(
        'GLOBAL_POSITION_INT',
        lat=-353632610, lon=1491652300, alt=584000,
        relative_alt=50000, vx=100, vy=-50, vz=10
    )
    batt_msg = MockMsg(
        'BATTERY_STATUS',
        voltage=12600, current_battery=200, battery_remaining=85
    )

    # Route both messages under the same Inode
    switch.route(gps_msg, inode, test_wall_ns)
    switch.route(batt_msg, inode, test_wall_ns)
    logger.info(f"Messages routed for inode {inode}")

    # ------------------------
    # SQL Verification
    # ------------------------
    with duckdb.connect(DB_PATH) as conn:
        res = conn.execute("""
            SELECT n.lat, n.lon, s.voltage, s.current_battery
            FROM nav_gps n
            JOIN sys_status s ON n.inode = s.inode
            WHERE n.inode = ?
        """, (inode,)).fetchone()

        if res:
            logger.info(f"✅ CONTRACT VERIFIED: Lat {res[0]}, Lon {res[1]}, Volt {res[2]}, Current {res[3]} on Inode {inode}")
            print(f"✅ CONTRACT VERIFIED: Lat {res[0]}, Lon {res[1]}, Volt {res[2]}, Current {res[3]} on Inode {inode}")
        else:
            logger.error(f"❌ JOIN FAILED: Check if both materializers wrote to the same Inode {inode}")
            print(f"❌ JOIN FAILED: Check if both materializers wrote to the same Inode {inode}")

# ----------------------------
# Main Entry
# ----------------------------
if __name__ == "__main__":
    logger.info("Starting Horizontal Connect Test")
    test_horizontal_connect()
    logger.info("Horizontal Connect Test Completed")

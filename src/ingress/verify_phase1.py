import time
import duckdb
from ingress.data_manager import DataManager
from ingress.ingress_switch import IngressSwitch
from ingress.domain_decoders import NavDecoder
from ingress.sys_decoder import SysDecoder
from ingress.materializers import NavMaterializer, SysMaterializer

class MockMsg:
    def __init__(self, m_type, **kwargs):
        self._type = m_type
        for k, v in kwargs.items(): setattr(self, k, v)
    def get_type(self): return self._type

def test_horizontal_connect():
    DB_PATH = "bin/nav_domain.db"
    LOG_DIR = "ingress/bin"

    # 1. Initialize Contract-Compliant Components
    dm = DataManager(LOG_DIR, DB_PATH)
    nav_mat = NavMaterializer(DB_PATH)
    sys_mat = SysMaterializer(DB_PATH)

    switch = IngressSwitch(
        nav_decoder=NavDecoder(nav_mat),
        sys_decoder=SysDecoder(sys_mat)
    )

    # 2. Atomic Identity Gate
    test_wall_ns = time.time_ns()
    inode, _ = dm.write_bronze_with_anchor(b"HORIZONTAL_TEST_DATA", test_wall_ns)

    print(f"--- Dispatching Inode {inode} ---")

    # 3. Simulated Horizontal Burst (One Inode, Two Domains)
    gps_msg = MockMsg('GPS_RAW_INT', lat=-353632610, lon=1491652300, alt=584000)
    batt_msg = MockMsg('BATTERY_STATUS', voltages=[12600], current_battery=200)

    # Route both messages under the SAME Inode
    switch.route(gps_msg, inode, test_wall_ns)
    switch.route(batt_msg, inode, test_wall_ns)

    # 4. SQL Verification: The Join Proof
    with duckdb.connect(DB_PATH) as conn:
        res = conn.execute("""
            SELECT n.lat, s.voltage
            FROM nav_gps n
            JOIN sys_status s ON n.inode = s.inode
            WHERE n.inode = ?
        """, (inode,)).fetchone()

        if res:
            print(f"\n✅ CONTRACT VERIFIED: Lat {res[0]} JOINED with Volt {res[1]}V on Inode {inode}")
        else:
            print(f"\n❌ JOIN FAILED: Check if both materializers wrote to the same Inode {inode}")

if __name__ == "__main__":
    test_horizontal_connect()
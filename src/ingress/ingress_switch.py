import logging

# Setup logger for the switch
logger = logging.getLogger("INGRESS_SWITCH")
logger.setLevel(logging.INFO)

class IngressSwitch:
    """
    The Toll Booth for MAVLink messages.
    Optimized for high-velocity Parquet ingestion.
    """

    def __init__(self, nav_arch=None, sys_arch=None, att_arch=None):
        self.nav_arch = nav_arch
        self.sys_arch = sys_arch
        self.att_arch = att_arch

        # 🔥 Optimization: Using sets for O(1) lookups
        self._nav_types = {'GPS_RAW_INT', 'GLOBAL_POSITION_INT', 'LOCAL_POSITION_NED'}
        self._sys_types = {'BATTERY_STATUS', 'SYS_STATUS', 'POWER_STATUS'}

    def route(self, msg, inode, wall_ns):
        """
        Attaches identity and broadcasts to the correct domain.
        """
        try:
            # 1. Identity Tagging
            msg.inode = inode
            msg.wall_ns = wall_ns

            # 2. Extract type (Faster than hasattr/getattr combo)
            try:
                m_type = msg.get_type()
            except AttributeError:
                m_type = msg.msgid

            # 3. NAVIGATION DOMAIN
            if m_type in self._nav_types and self.nav_arch:
                self.nav_arch.ingest(msg)
                # logger.info(f"✔ Routed {m_type}") # KEEP COMMENTED FOR STRESS TEST

            # 4. SYSTEM DOMAIN
            elif m_type in self._sys_types and self.sys_arch:
                self.sys_arch.ingest(msg)
                # logger.info(f"✔ Routed {m_type}") # KEEP COMMENTED FOR STRESS TEST

        except Exception as e:
            logger.error(f"❌ IngressSwitch routing failed: {e}")
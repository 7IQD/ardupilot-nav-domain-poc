class IngressSwitch:
    def __init__(self, nav_decoder, sys_decoder):
        self.nav_decoder = nav_decoder
        self.sys_decoder = sys_decoder

    def route(self, msg, inode, wall_ns):
        """
        Broadcasting the Umbilical Cord.
        One Inode is passed to multiple domains to create Horizontal alignment.
        """
        # Contract: Attach identity to the object before any domain sees it
        msg.inode = inode
        msg.wall_ns = wall_ns

        m_type = msg.get_type()

        # 1. Navigation Domain - Extracts spatial state
        if m_type in ['GPS_RAW_INT', 'GLOBAL_POSITION_INT', 'LOCAL_POSITION_NED']:
            self.nav_decoder.process(msg)

        # 2. System Domain - Extracts health/power state
        if m_type in ['BATTERY_STATUS', 'SYS_STATUS', 'POWER_STATUS']:
            self.sys_decoder.process(msg)

    def route(self, msg_type, data):
    # PO Diagnostic
        if msg_type in ["GLOBAL_POSITION_INT", "BATTERY_STATUS"]:
            print(f"DEBUG: Switch Routing {msg_type} to Materializer. Data Keys: {list(data.keys())}")
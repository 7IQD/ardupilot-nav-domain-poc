class SysDecoder:
    def __init__(self, materializer):
        self.materializer = materializer

    def process(self, msg):
        m_type = msg.get_type()

        # Identity is already on the msg object via IngressSwitch
        data = {
            "inode": msg.inode,
            "voltage": getattr(msg, 'voltages', [0])[0] / 1000.0 if m_type == 'BATTERY_STATUS' else None,
            "current": getattr(msg, 'current_battery', -1) / 100.0 if m_type == 'BATTERY_STATUS' else None,
            "load": getattr(msg, 'load', None) if m_type == 'SYS_STATUS' else None
        }

        # Contract Validation Print
        if any(v is not None for k, v in data.items() if k != "inode"):
            print(f"   └── [SYS-FACT] Inode: {data['inode']} | Volt: {data['voltage']}V")
            self.materializer.write(data)
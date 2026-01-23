class NavDecoder:
    def __init__(self, materializer):
        self.materializer = materializer

    def process(self, msg):
        data = {
            "inode": msg.inode,
            "lat": getattr(msg, 'lat', None),
            "lon": getattr(msg, 'lon', None),
            "alt": getattr(msg, 'alt', None)
        }

        # Only log/write if we actually have data for this domain
        if data['lat'] is not None:
            print(f"   ├── [NAV-FACT] Inode: {data['inode']} | Lat: {data['lat']}")
            self.materializer.write(data)

class SysHealthDecoder:
    def __init__(self, materializer):
        self.materializer = materializer

    def process(self, msg):
        data = {
            "inode": msg.inode,
            "ts_usec": getattr(msg, "ts_usec", None),
            "voltage": getattr(msg, "voltage", None),
        }
        self.materializer.write(data)
        print(f"[SYS] Processed {msg.get_type()} | inode {msg.inode}")

class EstimatorDecoder:
    def __init__(self, materializer):
        self.materializer = materializer

    def process(self, msg):
        data = {
            "inode": msg.inode,
            "ts_usec": getattr(msg, "ts_usec", None),
        }
        self.materializer.write(data)
        print(f"[EST] Processed {msg.get_type()} | inode {msg.inode}")

class DefaultLoggerDecoder:
    def process(self, msg):
        print(f"[DEFAULT] Logged {msg.get_type()} | inode {getattr(msg, 'inode', None)}")

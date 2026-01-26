import logging
logger = logging.getLogger("nav_decoder_clerk")

class nav_decoder_clerk:
    def __init__(self, materializer):
        self.materializer = materializer

    def process(self, msg):
        data = {
            "inode": msg.inode,
            "lat": getattr(msg, 'lat', None),
            "lon": getattr(msg, 'lon', None),
            "alt": getattr(msg, 'alt', None)
        }
        if data['lat'] is not None:
            logger.info(f"[NAV-FACT] Inode: {data['inode']} | Lat: {data['lat']}")
            self.materializer.write(data)

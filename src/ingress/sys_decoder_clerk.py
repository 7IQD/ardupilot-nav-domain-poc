import logging
logger = logging.getLogger("sys_decoder_clerk")

class sys_decoder_clerk:
    def __init__(self, materializer):
        self.materializer = materializer

    def process(self, msg):
        """
        Processes system messages (SYS_STATUS, BATTERY_STATUS, POWER_STATUS)
        and writes to the materializer with traceable logging.
        """
        data = {
            "inode": getattr(msg, "inode", None),
            "ts_usec": getattr(msg, "ts_usec", None),
            "voltage": getattr(msg, "voltage", None),
            "current": getattr(msg, "current", None),
            "battery_remaining": getattr(msg, "battery_remaining", None),
        }

        self.materializer.write(data)
        logger.info(f"[SYS] Processed {msg.get_type()} | inode {data['inode']}")

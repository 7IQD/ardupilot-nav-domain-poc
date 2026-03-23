import json
from pathlib import Path

class DFActionMap:
    """
    Domain routing service for ArduPilot telemetry.
    Loads a JSON policy and assigns domains to MsgTypes.
    """

    def __init__(self, json_path=None):
        # Default path: next to this file
        self.json_path = Path(json_path or Path(__file__).parent / "FMT_Library.json")
        with open(self.json_path, "r") as f:
            self.policy = json.load(f)

        # Flatten for quick lookup: MsgType -> domain
        self.msg_to_domain = {}
        for domain, msgs in self.policy.items():
            for msg in msgs.keys():
                self.msg_to_domain[msg.upper()] = domain

    def get_domains(self):
        return ["NAV_DOMAIN", "EST_DOMAIN", "POWER_DOMAIN", "COM_DOMAIN", "SYS_DOMAIN"]

    def get_domain_for_msg(self, msg_name):
        """
        Returns the domain for a given MsgType, defaulting to SYS_DOMAIN.
        """
        n = msg_name.upper()
        return self.msg_to_domain.get(n, "SYS_DOMAIN")
from .nav_decoder_clerk import NavDecoder, SysHealthDecoder, EstimatorDecoder, DefaultLoggerDecoder
# Import or create CommDecoder
from .comm_decoder_clerk import CommDecoder

class ActionMap:
    def __init__(self, switch, materializers, active_domains=None):
        self.switch = switch
        self.materializers = materializers
        # Default includes NAV and COM for live setup
        self.active_domains = active_domains or ['NAV', 'COM']
        self.default_decoder = DefaultLoggerDecoder()
        self.switch.default_decoder = self.default_decoder

        # MAVLink message IDs for each domain (priority, freq)
        self.domain_msgids = {
            'NAV': [(24, 'HIGH', 5), (30, 'HIGH', 50), (32, 'MEDIUM', 20), (193, 'LOW', 1)],
            'SYS': [(0, 'HIGH', 1), (2, 'MEDIUM', 1), (147, 'MEDIUM', 5), (241, 'LOW', 10)],
            'ESTIMATOR': [(27, 'HIGH', 50), (116, 'HIGH', 50), (129, 'HIGH', 50), (136, 'LOW', 1)],
            'COM': [(150, 'HIGH', 50), (151, 'MEDIUM', 20), (152, 'LOW', 5)]  # Communication domain messages
        }

        # Domain decoders
        self.domain_decoders = {
            'NAV': NavDecoder,
            'SYS': SysHealthDecoder,
            'ESTIMATOR': EstimatorDecoder,
            'COM': CommDecoder,
        }

        # Cross-domain messages (optional)
        self.cross_domain_msgids = {147: ['SYS', 'NAV']}

    def register_all(self):
        for domain, msg_list in self.domain_msgids.items():
            if domain not in self.active_domains:
                continue
            decoder_cls = self.domain_decoders[domain]
            materializer = self.materializers.get(domain)
            for msgid_tuple in msg_list:
                msgid = msgid_tuple[0]
                if msgid in self.cross_domain_msgids:
                    decoders = [
                        self.domain_decoders[d](self.materializers[d])
                        for d in self.cross_domain_msgids[msgid]
                        if d in self.active_domains
                    ]
                    self.switch.register(msgid, decoders)
                else:
                    self.switch.register(msgid, decoder_cls(materializer))
        print(f"[ActionMap] Registered active domains: {self.active_domains}")

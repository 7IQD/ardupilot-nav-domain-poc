from .nav_decoder_clerk import NavDecoder, SysHealthDecoder, EstimatorDecoder, DefaultLoggerDecoder
from .comm_decoder_clerk import CommDecoder
# Standardized import based on your src/ingress/ structure
from .power_decoder_clerk import PowerDecoder

class ActionMap:
    def __init__(self, switch, materializers, active_domains=None):
        self.switch = switch
        self.materializers = materializers

        # 1. Aligned to the 5 domains we discussed
        self.active_domains = active_domains or ['NAV', 'COM', 'SYS', 'ESTIMATOR', 'POWER']
        self.default_decoder = DefaultLoggerDecoder()
        self.switch.default_decoder = self.default_decoder

        # 2. MAVLink message IDs (Aligned with your existing IDs)
        self.domain_msgids = {
            'NAV': [(24, 'HIGH', 5), (30, 'HIGH', 50), (32, 'MEDIUM', 20), (193, 'LOW', 1)],
            'SYS': [(0, 'HIGH', 1), (2, 'MEDIUM', 1), (241, 'LOW', 10)],
            'ESTIMATOR': [(27, 'HIGH', 50), (116, 'HIGH', 50), (129, 'HIGH', 50), (136, 'LOW', 1)],
            'COM': [(150, 'HIGH', 50), (151, 'MEDIUM', 20), (152, 'LOW', 5)],
            'POWER': [(1, 'HIGH', 1), (147, 'HIGH', 10)]
        }

        self.domain_decoders = {
            'NAV': NavDecoder,
            'SYS': SysHealthDecoder,
            'ESTIMATOR': EstimatorDecoder,
            'COM': CommDecoder,
            'POWER': PowerDecoder,
        }

        # 3. Cross-domain logic preserved
        self.cross_domain_msgids = {147: ['SYS', 'NAV', 'POWER']}

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

        print(f"[ActionMap] Registered 5 active domains: {self.active_domains}")

    # --- THE GAP CLOSER ---
    def get_columns_for_domain(self, domain_name):
        """
        Returns the canonical columns from the materializer.
        This is the method the Refiner uses to avoid 'SELECT *'.
        """
        # Simple lookup without adding new complex logic
        lookup = domain_name.upper()
        if lookup == 'EST': lookup = 'ESTIMATOR'

        materializer = self.materializers.get(lookup)
        if materializer and hasattr(materializer, 'canonical_columns'):
            return materializer.canonical_columns

        return []
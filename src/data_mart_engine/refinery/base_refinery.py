from abc import ABC, abstractmethod
import logging

class BaseRefinery(ABC):
    def __init__(self, config: dict):
        self.config = config
        self.silver_path = config.get('silver_path')
        self.gold_path = config.get('gold_path')
        self.domain = config.get('domain', 'GENERIC')

    @abstractmethod
    def load_context(self):
        """
        Hook 1: Pull the relevant physical partition from Silver.
        Must return a data structure (e.g., DataFrame) or raise Error.
        """
        pass

    @abstractmethod
    def transform(self, data):
        """
        Hook 2: The 'Think' phase.
        Apply domain-specific math/logic to the loaded context.
        """
        pass

    @abstractmethod
    def emit(self, refined_data):
        """
        Hook 3: The 'Materialization' phase.
        Write the refined truth to the Gold Mart.
        """
        pass

    def run_pulse(self):
        """
        The Invariant Lifecycle.
        This is the only method main.py should ever call.
        """
        logging.info(f"--- {self.domain} Pulse Started ---")
        try:
            data = self.load_context()
            if data is not None and not data.empty:
                refined = self.transform(data)
                self.emit(refined)
                logging.info(f"--- {self.domain} Pulse Completed ---")
                return True
            logging.warning(f"--- {self.domain} Pulse Skipped: No Data ---")
            return False
        except Exception as e:
            logging.error(f"--- {self.domain} Pulse Failed: {e} ---")
            raise e
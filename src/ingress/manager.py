import os
import logging
from data_manager import data_manager  # lowercase to match updated class

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/maintenance.log',
    level=logging.INFO,
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("maintenance")

def perform_maintenance():
    print("--- System Manager Mode ---")

    # Initialize DataManager
    db = data_manager(log_dir="bin", db_path="bin/anchor_registry.db")

    # Check if Bronze Ledger exists
    if os.path.exists(db.bin_path):
        size = os.path.getsize(db.bin_path)
        print(f"Current Bronze Ledger Size: {size} bytes")
        logger.info(f"Bronze Ledger found. Size: {size} bytes")
    else:
        print("No Bronze Ledger found.")
        logger.warning("Bronze Ledger not found.")

    # Optionally overwrite/reset the database
    choice = input("Do you want to overwrite/reset the database? (y/n): ")
    if choice.lower() == 'y':
        # Reset logic: remove Bronze ledger and reinitialize AnchorRegistry
        try:
            if os.path.exists(db.bin_path):
                os.remove(db.bin_path)
                logger.info("Bronze Ledger removed for fresh start.")
            db.anchor_reg.reset_registry()
            logger.info("Anchor Registry reset successfully.")
            print("Database has been wiped for a fresh test.")
        except Exception as e:
            logger.error(f"Failed to reset database: {e}")
            print(f"Error during reset: {e}")

if __name__ == "__main__":
    perform_maintenance()

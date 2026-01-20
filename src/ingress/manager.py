import os
from data_manager import DataManager # Match the filename exactly

def perform_maintenance():
    print("--- System Manager Mode ---")
    db = DataManager(base_name="flight_test", folder="bin")

    # Check if files exist
    if os.path.exists(db.bin_path):
        size = os.path.getsize(db.bin_path)
        print(f"Current Database Size: {size} bytes")
    else:
        print("No database found.")

    # Option to manually trigger your 'Overwrite' requirement
    choice = input("Do you want to overwrite/reset the database? (y/n): ")
    if choice.lower() == 'y':
        db.initialize_storage(overwrite=True)
        print("Database has been wiped for a fresh test.")

if __name__ == "__main__":
    perform_maintenance()
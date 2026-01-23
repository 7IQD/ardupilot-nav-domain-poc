import sys
import os
from multiprocessing import Process, Queue

# Ensure the 'src' directory is in the path so we can import 'ingress'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ingress.sim_vehicle_ingress import run_ingress
from ingress.materializers import NavDuckDBMaterializer

def start_architect(queue):
    try:
        # PATH CORRECTION:
        # db is in bin/, mapping is in ingress/
        architect = NavDuckDBMaterializer(
            db_path="bin/nav_domain.db",
            mapping_path="bin/mapping.json"
        )

        print("👤 ARCHITECT: System Online. Monitoring Vault...")

        while not architect.is_quarantined:
            packet = queue.get()
            architect.ingest(packet)

            if packet['inode'] % 50 == 0:
                print(f"🏛️  SILVER COMMIT: Inode {packet['inode']}")

    except Exception as e:
        print(f"❌ ARCHITECT ERROR: {e}")

if __name__ == "__main__":
    shared_queue = Queue()

    clerk_proc = Process(target=run_ingress, args=(shared_queue,))
    architect_proc = Process(target=start_architect, args=(shared_queue,))

    print("🛰️  SITL TELEMETRY ENGINE: STARTING...")

    try:
        architect_proc.start()
        clerk_proc.start()

        clerk_proc.join()
        architect_proc.join()

    except KeyboardInterrupt:
        print("\n\n👋 Shutdown signal received...")
        shared_queue.cancel_join_thread() # Fixes the threading error you saw
        clerk_proc.terminate()
        architect_proc.terminate()
        print("✅ Pipeline Offline.")
import os
import shutil
import duckdb
import sys
import threading
import time
import logging

# --- LOGGER CONFIGURATION ---
# Provides a clean, timestamped record for debugging missions.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("clerk_mission.log"), # Persistent log file
        logging.StreamHandler(sys.stdout)          # Console output
    ]
)
logger = logging.getLogger("Clerk")

class Clerk:
    def __init__(self):
        self.root_dir = "/home/ni/ardupilot-nav-domain-poc"
        self.vault_b = os.path.join(self.root_dir, 'bin/vault/vault_b')
        self.warehouse = os.path.join(self.root_dir, 'bin/vault/warehouse')

        os.makedirs(self.vault_b, exist_ok=True)
        os.makedirs(self.warehouse, exist_ok=True)
        logger.debug(f"Clerk initialized. Vault B: {self.vault_b}")

    def reset(self):
        """Sterilizes staging and warehouse per [2026-01-15]."""
        logger.warning("🚨 [CLEANING] Sterilizing Vault B and Warehouse...")
        for folder in [self.vault_b, self.warehouse]:
            if not os.path.exists(folder): continue
            for f in os.listdir(folder):
                path = os.path.join(folder, f)
                try:
                    if os.path.isfile(path): os.remove(path)
                    elif os.path.isdir(path): shutil.rmtree(path)
                except Exception as e:
                    logger.error(f"Failed to delete {path}: {e}")
        logger.info("✅ Clerk reset successful.")

    def commit(self, domain, source_type="sitl"):
        """
        Consolidates fragments with full traceability.
        source_type: 'sitl' or 'dflog'
        """
        # Debugger friendly pathing: specific mission files
        master_path = os.path.join(self.warehouse, f"{domain}_{source_type}_master.parquet")
        prefix = f"{domain}_raw_"
        fragment_pattern = os.path.join(self.vault_b, f"{prefix}*.parquet")

        # Explicit fragment detection
        fragments = [f for f in os.listdir(self.vault_b) if f.startswith(prefix)]
        if not fragments:
            logger.debug(f"Domain [{domain}]: No fragments found. Skipping.")
            return

        logger.info(f"📦 [COMMIT] Domain: {domain} | Mission: {source_type} | Count: {len(fragments)}")

        # Heartbeat for long-running DuckDB tasks
        stop_heartbeat = False
        def heartbeat():
            while not stop_heartbeat:
                time.sleep(1)
                logger.debug(f"... Consolidating {domain} ...")

        t = threading.Thread(target=heartbeat)
        t.start()

        try:
            con = duckdb.connect(':memory:') # Use clean memory for each commit
            if not os.path.exists(master_path):
                logger.info(f"🆕 Creating new master: {master_path}")
                con.execute(f"""
                    COPY (
                        SELECT * FROM read_parquet('{fragment_pattern}')
                        ORDER BY inode ASC
                    ) TO '{master_path}' (FORMAT 'PARQUET')
                """)
            else:
                logger.info(f"🔄 Appending to master: {master_path}")
                temp_path = f"{master_path}.tmp"
                con.execute(f"""
                    COPY (
                        SELECT * FROM (
                            SELECT * FROM read_parquet('{master_path}')
                            UNION ALL
                            SELECT * FROM read_parquet('{fragment_pattern}')
                        )
                        QUALIFY ROW_NUMBER() OVER (PARTITION BY inode ORDER BY wall_ns DESC) = 1
                        ORDER BY inode ASC
                    ) TO '{temp_path}' (FORMAT 'PARQUET')
                """)
                os.replace(temp_path, master_path)
        except Exception as e:
            logger.error(f"❌ [CRITICAL] DuckDB Fail on {domain}: {e}")
            raise
        finally:
            stop_heartbeat = True
            t.join()

    def finalize_run(self, is_real_flight=False):
        """
        Finalizes the mission.
        is_real_flight: True (dflog) | False (sitl)
        """
        mission = "dflog" if is_real_flight else "sitl"
        logger.info(f"🏁 [CLERK] Starting {mission.upper()} Finalization Suite")

        for domain in ['nav', 'sys', 'com', 'est']:
            try:
                self.commit(domain, source_type=mission)
            except Exception as e:
                logger.error(f"Failed {domain} commit: {e}")

        # Final cleanup with verification
        logger.info("🧹 [CLEANUP] Clearing Vault B staging area...")
        for f in os.listdir(self.vault_b):
            if f.endswith(".parquet"):
                os.remove(os.path.join(self.vault_b, f))

        logger.info(f"✅ Mission {mission.upper()} finalized. Warehouse locked.")
import duckdb, os, glob, time, signal, sys, logging
from logging.handlers import RotatingFileHandler

# --- PORTABLE PATH RESOLUTION ---
ABS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BIN_DIR = os.path.join(ABS_ROOT, "bin", "vault")
LOG_DIR = os.path.join(ABS_ROOT, "logs")

log_file = os.path.join(LOG_DIR, "vault_activity.log")
log_handler = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=3)
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(name)-10s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', handlers=[log_handler])
logger = logging.getLogger("HUD")

running = True
def handle_exit(s, f):
    logger.info("SIGNAL: Termination received.")
    global running
    running = False

signal.signal(signal.SIGINT, handle_exit)

def process_segment(path):
    filename = os.path.basename(path)
    try:
        conn = duckdb.connect(path, read_only=True)
        res = conn.execute("SELECT MAX(inode), COUNT(*) FROM nav_gps").fetchone()
        conn.close()
        if res and res[1] > 0:
            logger.info(f"INGESTED segment: {filename} | MaxInode: {res[0]} | Packets: {res[1]}")
        os.remove(path)
        logger.info(f"PURGED segment: {filename} from vault.")
    except Exception:
        pass

def run_relay_hud():
    logger.info(f"HUD_START: Monitoring {BIN_DIR}")
    while running:
        segs = sorted(glob.glob(os.path.join(BIN_DIR, "nav_seg_*.db")))
        if len(segs) > 1:
            for p in segs[:-1]: process_segment(p)
        time.sleep(1)

    # Final sweep
    time.sleep(0.5)
    for p in sorted(glob.glob(os.path.join(BIN_DIR, "nav_seg_*.db"))):
        process_segment(p)
    logger.info("HUD_STOP: Vault cleared.")
    sys.exit(0)

if __name__ == "__main__":
    run_relay_hud()
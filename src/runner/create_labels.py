import logging
import argparse
import duckdb
from pathlib import Path

# Disciplined Import: Only the Controller/Labeler is exposed to the runner
from src.df_domain_data_services.nav.nav_labeler import NavLabeler

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).resolve().parent.parent.parent / "bin/vault/drone_df_views.db"

def main(mission_ids):
    if not DB_PATH.exists():
        logger.error(f"Database missing at {DB_PATH}")
        return

    conn = duckdb.connect(str(DB_PATH))

    # Registry of active domains (Scalable to EST, SYS, POWER, etc.)
    active_domain_labelers = [NavLabeler]

    for mid in mission_ids:
        logger.info(f"\n🚀 Starting Domain Labeling for Mission: {mid}")
        for labeler_class in active_domain_labelers:
            try:
                # Initialize and Run
                instance = labeler_class(mid, conn)
                count = instance.execute_pipeline()
                logger.info(f"✅ {labeler_class.__name__}: Committed {count} windows.")
            except Exception as e:
                logger.error(f"❌ {labeler_class.__name__} Failed: {e}")

    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GSoC Domain Labeling Pipeline")
    parser.add_argument("--missions", nargs="+", required=True, help="Mission IDs")
    args = parser.parse_args()
    main(args.missions)
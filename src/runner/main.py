import sys
import os

# Ensuring the root is in path
sys.path.append(os.getcwd())

from src.vault.clerk import Clerk
from src.ingress.nav_architect import NavArchitect
from src.ingress.sys_architect import SysArchitect
from src.runner.orchestrator import Orchestrator

def main():
    # 1. Initialize the Clerk
    clerk = Clerk()

    # 2. Reset the Vault (Overwrite Requirement)
    clerk.reset_vault()

    try:
        # 3. Setup Recorders
        nav_arch = NavArchitect(limit=50)
        sys_arch = SysArchitect(limit=25)

        # 4. Run the Engine (Action Map Gates)
        engine = Orchestrator(nav_arch, sys_arch)
        engine.run()

    finally:
        # 5. Logical Conclusion (Complete File Consolidation)
        print("🏁 [POC] Run finished. Consolidating warehouse...")
        clerk.finalize_run()

if __name__ == "__main__":
    main()
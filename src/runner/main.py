import sys
import os

# Internal Imports
from src.runner.orchestrator import Orchestrator
from src.ingress.nav_architect import NavArchitect
from src.ingress.sys_architect import SysArchitect
from src.vault.clerk import Clerk
from src.scripts.report_generator import ReportGenerator  # Added for post-run analytics

def main():
    print("\n" + "="*50)
    print("🛰️  ArduPilot Nav-Domain POC | Marathon Mode")
    print("="*50)

    # 1️⃣ Initialize Clerk (The Librarian)
    clerk = Clerk()

    # 2️⃣ Safety Gate: Choice of Mission Persistence
    print("\n[DATABASE CONFIGURATION]")
    choice = input("👉 Start FRESH mission? (Wipes Warehouse) [y/N]: ").strip().lower()

    if choice == 'y':
        print("🗑️  Resetting Warehouse... Starting from Inode 0.")
        clerk.reset()
    else:
        print("⚠️  CONTINUING: Preserving Warehouse. New data will append.")

    # 3️⃣ Setup Architects (Bronze Layer)
    nav_arch = NavArchitect(limit=50)
    sys_arch = SysArchitect(limit=25)

    # 4️⃣ Initialize Engine (The Universal Spine)
    engine = Orchestrator(nav_arch, sys_arch)

    try:
        print("\n🚀 [ENGINE] Starting Ground Run...")
        print("💡 Press Ctrl+C to stop recording and finalize warehouse.\n")
        engine.run()

    except KeyboardInterrupt:
        print("\n\n🛑 [ENGINE] Stopping via User Interrupt...")

    except Exception as e:
        print(f"\n❌ [CRITICAL ERROR]: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 5️⃣ Finalize: Commit fragments into master files
        print("\n" + "-"*50)
        print("🏁 [POC] Run finished. Finalizing vaulting...")

        try:
            clerk.finalize_run()

            # 6️⃣ Generate Mission Report (The Automatic Debrief)
            print("\n📊 [REPORT] Generating Post-Run Health Metrics...")
            rg = ReportGenerator()
            rg.generate_all()

            print("✅ Warehouse Updated & Reported. System Safe for Shutdown.")
        except Exception as finalize_error:
            print(f"⚠️  Warning: Finalization or Reporting failed: {finalize_error}")

        print("-"*50 + "\n")

if __name__ == "__main__":
    main()
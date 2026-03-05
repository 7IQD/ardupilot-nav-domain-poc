import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os

class NavDashboard:
    def __init__(self, gold_path, fence_limit=2.0):
        self.gold_path = gold_path
        self.fence_limit = fence_limit
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(10, 5))
        self.ln, = self.ax.plot([], [], color='#00E676', lw=2, label='Drift Error (m)')
        self.fence_ln = self.ax.axhline(y=self.fence_limit, color='red', ls='--', alpha=0.5, label='Safety Fence')

    def update(self, frame):
        if not os.path.exists(self.gold_path):
            return self.ln,
        try:
            df = pd.read_parquet(self.gold_path)
            if df.empty: return self.ln,

            view = df.tail(50).reset_index()
            latest = view['precision_error_m'].iloc[-1]

            self.ln.set_data(view.index, view['precision_error_m'])

            # IMPROVED SCALING: Focuses on the data while keeping fence visible
            current_max = view['precision_error_m'].max()
            self.ax.set_ylim(-0.01, max(current_max * 1.5, 0.1)) # Zooms in on the cm-level noise
            self.ax.set_xlim(0, 50)

            self.ax.set_title(f"NAV MONITOR LIVE | Latest: {latest:.4f}m", fontsize=12)
        except Exception:
            pass
        return self.ln,

    def run(self):
        ani = FuncAnimation(self.fig, self.update, interval=1000, cache_frame_data=False)
        plt.legend(loc='upper right')
        plt.ylabel("Meters (Error)")
        plt.show()

if __name__ == "__main__":
    # Adjust path based on where you are running the script
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    GOLD = os.path.join(BASE_DIR, "bin/vault/gold/fact_nav_precision.parquet")
    NavDashboard(GOLD).run()
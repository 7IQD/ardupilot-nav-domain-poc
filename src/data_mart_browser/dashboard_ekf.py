import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
import sys

def run_graphical_dashboard(mission_id):
    # Construct absolute path to the Gold data mart
    gold_path = os.path.expanduser(
        f"~/ardupilot-nav-domain-poc/bin/vault/gold/nav_ekf/{mission_id}/fact_nav_precision.parquet"
    )

    # --- Figure Setup ---
    # Fallback logic for Matplotlib style compatibility
    try:
        plt.style.use('seaborn-v0_8-darkgrid')
    except:
        plt.style.use('ggplot')

    fig, ax = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    fig.suptitle(f"📡 Mission: {mission_id} | EKF Precision (Live)", fontsize=14)

    # Data buffers for sliding window visualization
    times, lat_errs, lon_errs, alt_errs = [], [], [], []
    last_processed_ts = 0  # Prevents duplicate plotting if data hasn't refreshed

    def update(frame):
        nonlocal last_processed_ts
        if not os.path.exists(gold_path):
            return

        try:
            # Load the latest refined facts from the Gold layer
            df = pd.read_parquet(gold_path, engine='pyarrow')
            if df.empty:
                return

            latest = df.iloc[-1]
            current_ts = latest['timestamp_ms']

            # Only append new data points to the buffer
            if current_ts > last_processed_ts:
                times.append(pd.to_datetime(current_ts, unit='ms'))
                lat_errs.append(latest['lat_err_deg'])
                lon_errs.append(latest['lon_err_deg'])
                alt_errs.append(latest['alt_err_m'])
                last_processed_ts = current_ts

            # Maintain a sliding window of the last 50 samples
            t_plot = times[-50:]
            la_plot, lo_plot, al_plot = lat_errs[-50:], lon_errs[-50:], alt_errs[-50:]

            if not t_plot:
                return

            datasets = [la_plot, lo_plot, al_plot]
            titles = ['Lat Error (deg)', 'Lon Error (deg)', 'Alt Error (m)']
            colors = ['tab:blue', 'tab:orange', 'tab:green']

            # Thresholds for visual "Stability" alerts
            thresholds = [0.000005, 0.000005, 0.05]

            for i in range(3):
                ax[i].cla()
                ax[i].plot(t_plot, datasets[i], color=colors[i], marker='.', markersize=6)
                ax[i].set_ylabel(titles[i])
                ax[i].grid(True, alpha=0.3)

                # Dynamic y-axis scaling with a small margin for visibility
                min_val, max_val = min(datasets[i]), max(datasets[i])
                margin = max((max_val - min_val) * 0.2, 1e-8)
                ax[i].set_ylim(min_val - margin, max_val + margin)

                # Real-time Status Labeling
                last_val = datasets[i][-1]
                is_stable = last_val < thresholds[i]

                # Format decimals: higher precision for Lat/Lon
                val_str = f"{last_val:.8f}" if i < 2 else f"{last_val:.3f}"
                status_text = "STABLE" if is_stable else "DRIFTING"

                ax[i].text(
                    t_plot[-1], last_val,
                    f" {val_str} ({status_text})",
                    color='green' if is_stable else 'red',
                    fontweight='bold',
                    va='bottom'
                )

            ax[2].set_xlabel("Timestamp (UTC)")
            plt.xticks(rotation=45)
            plt.tight_layout(rect=[0, 0.03, 1, 0.95])

        except Exception:
            # Skip frame if file is locked during a Refinery write operation
            pass

    # Update every 2 seconds to match the Refinery cadence
    ani = animation.FuncAnimation(fig, update, interval=2000, cache_frame_data=False)
    plt.show()

if __name__ == "__main__":
    # Allow Mission ID to be passed as an argument, default to MARATHON_01
    m_id = sys.argv[1] if len(sys.argv) > 1 else "MARATHON_01"
    run_graphical_dashboard(m_id)
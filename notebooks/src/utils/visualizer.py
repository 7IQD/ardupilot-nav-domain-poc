import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

class UniversalVisualizer:
    @staticmethod
    def plot_defragmentation_river(df_raw, df_gold, params):
        plt.style.use('fast')
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8), sharey=True)
        colors = plt.cm.tab10.colors

        # BEFORE
        for i, p in enumerate(params):
            if p in df_raw.columns:
                raw_series = df_raw[p].dropna()
                ax1.scatter([i] * len(raw_series), raw_series.index, marker='s', s=100, alpha=0.5, color=colors[i % 10])
        ax1.set_title("RAW FRAGMENTATION", fontweight='bold')
        ax1.set_xticks(range(len(params)))
        ax1.set_xticklabels(params, rotation=45)
        ax1.invert_yaxis()

        # AFTER
        for i, p in enumerate(params):
            ax2.scatter([i] * len(df_gold), df_gold.index, marker='s', s=100, alpha=1.0, color=colors[i % 10], edgecolor='white')
        ax2.set_title("ALIGNED & RECONSTRUCTED", fontweight='bold', color='green')
        ax2.set_xticks(range(len(params)))
        ax2.set_xticklabels(params, rotation=45)

        plt.tight_layout()
        return fig

    @staticmethod
    def plot_3d_forensic(df, mission_id):
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')
        drift = (df['RelHomeAlt'] - df['RelOriginAlt']).abs()
        p = ax.scatter(df['Lng'], df['Lat'], df['RelOriginAlt'], c=drift, cmap='YlOrRd', s=10)
        ax.set_title(f"3D Path Analysis: {mission_id}")
        fig.colorbar(p, label="Drift (m)")
        plt.show()
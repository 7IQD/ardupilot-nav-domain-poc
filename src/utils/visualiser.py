import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class UniversalVisualizer:
    @staticmethod
    def plot(df, domain, mission_id=None, kind=None, params=None):
        """
        Universal plotting for multiple domains.
        domain: 'NAV', 'EST', 'SYS', 'POWER', 'COM'
        kind: optional, defaults per domain
        params: list of columns for defrag/line plots
        """
        domain = domain.upper()
        if domain == "NAV":
            if kind is None:
                kind = "defrag_river"
            if kind == "defrag_river":
                if params is None:
                    # Pick first 3 numeric columns
                    params = df.select_dtypes(include="number").columns[:3].tolist()
                UniversalVisualizer._plot_defrag_river(df_raw=df, df_gold=df, params=params)
            elif kind == "3d_forensic":
                UniversalVisualizer._plot_3d_forensic(df, mission_id)
        elif domain == "EST":
            if kind is None:
                kind = "line_series"
            UniversalVisualizer._plot_line_series(df, params)
        elif domain == "SYS":
            if kind is None:
                kind = "histogram"
            UniversalVisualizer._plot_histogram(df, params)
        elif domain == "POWER":
            if kind is None:
                kind = "line_series"
            UniversalVisualizer._plot_line_series(df, params)
        elif domain == "COM":
            if kind is None:
                kind = "scatter_map"
            UniversalVisualizer._plot_scatter_map(df, params)
        else:
            raise ValueError(f"Unknown domain: {domain}")

    @staticmethod
    def _plot_defrag_river(df_raw, df_gold, params):
        plt.style.use('fast')
        fig, (ax1, ax2) = plt.subplots(1,2,figsize=(15,8), sharey=True)
        colors = plt.cm.tab10.colors
        for i,p in enumerate(params):
            if p in df_raw.columns:
                ax1.scatter([i]*len(df_raw), df_raw.index, s=100, alpha=0.5, color=colors[i%10])
                ax2.scatter([i]*len(df_gold), df_gold.index, s=100, alpha=1.0, color=colors[i%10], edgecolor='white')
        ax1.set_title("RAW FRAGMENTATION", fontweight='bold'); ax1.invert_yaxis()
        ax2.set_title("ALIGNED & RECONSTRUCTED", fontweight='bold', color='green')
        plt.tight_layout(); plt.show()

    @staticmethod
    def _plot_3d_forensic(df, mission_id):
        fig = plt.figure(figsize=(10,7))
        ax = fig.add_subplot(111, projection='3d')
        drift = (df['RelHomeAlt'] - df['RelOriginAlt']).abs()
        p = ax.scatter(df['Lng'], df['Lat'], df['RelOriginAlt'], c=drift, cmap='YlOrRd', s=10)
        ax.set_title(f"3D Path Analysis: {mission_id}")
        fig.colorbar(p, label="Drift (m)")
        plt.show()

    @staticmethod
    def _plot_line_series(df, params):
        if params is None:
            params = df.select_dtypes(include="number").columns[:2].tolist()
        plt.figure(figsize=(12,6))
        for p in params:
            plt.plot(df.index, df[p], label=p)
        plt.title("Line Series Plot")
        plt.legend(); plt.grid(True); plt.show()

    @staticmethod
    def _plot_histogram(df, params):
        if params is None:
            params = df.select_dtypes(include="number").columns[:2].tolist()
        df[params].hist(figsize=(10,5), bins=20, layout=(1, len(params))); plt.show()

    @staticmethod
    def _plot_scatter_map(df, params):
        if params is None:
            params = df.select_dtypes(include="number").columns[:2].tolist()
        plt.figure(figsize=(10,6))
        plt.scatter(df[params[0]], df[params[1]], alpha=0.7)
        plt.title("Scatter Map"); plt.xlabel(params[0]); plt.ylabel(params[1]); plt.grid(True); plt.show()
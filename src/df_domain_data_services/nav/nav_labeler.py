"""
NavLabeler — Phase-Aware Forensic Labeling for NAV Domain
"""

import pandas as pd
import numpy as np


def detect_phase(df, takeoff_window=15e6, landing_window=15e6):
    """
    Lightweight phase detection using Altitude and timestamps.
    Phases: Pre-Flight, Takeoff, Cruise, Landing, Post-Flight
    """

    df = df.copy().sort_values("TimeUS").reset_index(drop=True)

    if 'Alt' not in df.columns:
        df['phase'] = 'UNKNOWN'
        return df

    df['is_airborne'] = df['Alt'] > 2.0

    if not df['is_airborne'].any():
        df['phase'] = 'PRE_FLIGHT'
        return df

    airborne_start = df.index[df['is_airborne']].min()
    airborne_end   = df.index[df['is_airborne']].max()

    df['phase'] = 'CRUISE'
    df.loc[:airborne_start, 'phase'] = 'PRE_FLIGHT'

    takeoff_end = df.loc[airborne_start, 'TimeUS'] + takeoff_window
    df.loc[
        (df['TimeUS'] > df.loc[airborne_start, 'TimeUS']) &
        (df['TimeUS'] <= takeoff_end),
        'phase'
    ] = 'TAKEOFF'

    landing_start = df.loc[airborne_end, 'TimeUS'] - landing_window
    df.loc[
        (df['TimeUS'] >= landing_start) &
        (df['TimeUS'] < df.loc[airborne_end, 'TimeUS']),
        'phase'
    ] = 'LANDING'

    df.loc[airborne_end:, 'phase'] = 'POST_FLIGHT'

    return df


class NavLabeler:

    def __init__(self, mission_id: str, df: pd.DataFrame):
        self.mission_id = mission_id
        self.df = df.copy().sort_values("TimeUS").reset_index(drop=True)

    def _apply_forensic_rules(self):

        df = self.df.copy()
        df['label'] = 'HEALTHY'

        # ------------------------
        # GPS Critical Loss
        # ------------------------
        loss_mask = df['NSats'].isna() | (df['NSats'] == 0)
        df.loc[loss_mask, 'label'] = 'GPS_CRITICAL_LOSS'

        # ------------------------
        # GPS Degraded
        # ------------------------
        degraded_mask = (df['NSats'] > 0) & (df['NSats'] < 10)
        df.loc[degraded_mask & ~loss_mask, 'label'] = 'GPS_DEGRADED'

        # ------------------------
        # Position Jump Detection
        # ------------------------
        df['lat_delta'] = df['Lat'].diff().abs()
        df['lng_delta'] = df['Lng'].diff().abs()

        jump_mask = (
            (df['lat_delta'] > 0.001) |
            (df['lng_delta'] > 0.001)
        )

        df.loc[jump_mask & ~loss_mask, 'label'] = 'GPS_JUMP_DETECTED'

        self.df = df
        return df


    def get_event_summary(self, min_duration=0.1, merge_healthy_gap=0.5):

        df = self._apply_forensic_rules()

        df = df.sort_values('TimeUS').reset_index(drop=True)

        df['event_id'] = (df['label'] != df['label'].shift()).cumsum()

        summary = df.groupby(['event_id', 'label']).agg(
            start_t=('TimeUS', 'min'),
            end_t=('TimeUS', 'max'),
            start_lat=('Lat', 'first'),
            end_lat=('Lat', 'last'),
            count=('TimeUS', 'count'),
            jump_lat_sum=('lat_delta', 'sum'),
            jump_lng_sum=('lng_delta', 'sum')
        ).reset_index()

        summary['duration_sec'] = (summary['end_t'] - summary['start_t']) / 1e6

        summary['jump_magnitude'] = summary[
            ['jump_lat_sum', 'jump_lng_sum']
        ].max(axis=1)

        summary = summary[
            summary['duration_sec'] >= min_duration
        ].copy()

        # ------------------------
        # Merge short healthy gaps
        # ------------------------

        if merge_healthy_gap > 0:

            merged = []
            prev = None

            for _, row in summary.iterrows():

                row = row.to_dict()

                if prev is None:
                    prev = row
                    continue

                healthy_gap = (
                    row['label'] == 'HEALTHY' and
                    row['duration_sec'] <= merge_healthy_gap
                )

                if prev['label'] != 'HEALTHY' and healthy_gap:

                    prev['end_t'] = row['end_t']
                    prev['end_lat'] = row['end_lat']
                    prev['count'] += row['count']
                    prev['duration_sec'] = (
                        (prev['end_t'] - prev['start_t']) / 1e6
                    )

                else:
                    merged.append(prev)
                    prev = row

            if prev:
                merged.append(prev)

            summary = pd.DataFrame(merged)

        # ------------------------
        # Attach Phase Context
        # ------------------------

        if 'phase' in self.df.columns:

            def phase_lookup(row):

                window = self.df.loc[
                    (self.df['TimeUS'] >= row['start_t']) &
                    (self.df['TimeUS'] <= row['end_t']),
                    'phase'
                ]

                if window.empty:
                    return "UNKNOWN"

                return window.mode().iloc[0]

            summary['phase'] = summary.apply(
                phase_lookup,
                axis=1
            )

        else:
            summary['phase'] = 'UNKNOWN'

        return summary.reset_index(drop=True)


    def get_mission_scorecard(self, mode='mission'):

        if mode == 'forensic':
            return self.get_event_summary(
                min_duration=0,
                merge_healthy_gap=0
            )

        return self.get_event_summary(
            min_duration=0.1,
            merge_healthy_gap=0.5
        )
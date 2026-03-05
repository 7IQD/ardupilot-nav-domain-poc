import numpy as np
import pandas as pd

def normalize_inverse(values, worst, best):
    """Linearly maps values to a 0-100 score where 'best' is 100."""
    values = np.array(values, dtype=float)
    denom = (worst - best) if worst != best else 1.0
    score = 100 * (worst - values) / denom
    return np.clip(score, 0, 100)

def scale_coordinates(df: pd.DataFrame, columns=['Lat', 'Lng']):
    """
    ArduPilot Safety: Automatically detects and scales 10^7 integers.
    Standard decimal degrees never exceed 180.0.
    """
    df = df.copy()
    for col in columns:
        if col in df.columns and not df[col].empty:
            # If the max absolute value is > 180, it's definitely 10^7 format
            if df[col].abs().max() > 180.0:
                df[col] = df[col] / 1e7
    return df

def compute_stability_score(df: pd.DataFrame, cols=['Roll', 'Pitch'], window=10):
    """Calculates a health score based on rolling variance."""
    df = df.copy()
    for col in cols:
        if col in df.columns:
            # Rolling standard deviation: high variation = low stability
            rolling_std = df[col].rolling(window=window).std().fillna(0)
            # ArduPilot Heuristic: 10 degrees of jitter is a critical 'worst'
            df[f'{col.lower()}_stability'] = normalize_inverse(rolling_std, worst=10.0, best=0.0)
    return df

def get_mission_health(df: pd.DataFrame, mission_id: str):
    """Executive summary of the flight's health."""
    if df.empty: return {"status": "NO_DATA"}

    stability_cols = [c for c in df.columns if 'stability' in c]
    avg_stability = df[stability_cols].mean().mean() if stability_cols else 0

    # Check for core columns (Note: Using Hardware-Faithful names)
    max_alt = df['Alt'].max() if 'Alt' in df.columns else 0

    return {
        "mission_id": mission_id,
        "max_alt_m": round(max_alt, 2),
        "data_points": len(df),
        "stability_score": round(avg_stability, 1),
        "health_status": "GREEN" if avg_stability > 70 else "AMBER" if avg_stability > 40 else "RED"
    }

def diagnose_instability(df):
    """
    Forensic Heuristics: Suggests fixes based on telemetry patterns.
    """
    reasons = []
    if df.empty: return reasons

    # Heuristic 1: High Roll Jitter + Low Speed = Bad Tuning
    # Note: Column names 'Roll' and 'Spd' match our DuckDB Gold Layer
    if 'Roll' in df.columns and 'Spd' in df.columns:
        if df['Roll'].var() > 10 and df['Spd'].mean() < 2:
            reasons.append({
                "cause": "Mechanical Vibration / PID Oscillation",
                "fix": "Check motor balance and reduce 'Rate Roll P' by 15%.",
                "conf": 85
            })

    # Heuristic 2: Baro vs GPS divergence (Altitude Confidence)
    # ArduPilot logs 'Alt' (EKF) and 'BaroAlt' or 'GAlt'
    if 'Alt' in df.columns and 'BaroAlt' in df.columns:
        diff = (df['Alt'] - df['BaroAlt']).abs().max()
        if diff > 5:
            reasons.append({
                "cause": "Sensor Inconsistency (EKF vs Baro)",
                "fix": "Check for light or wind interference on the Barometer.",
                "conf": 90
            })

    return reasons
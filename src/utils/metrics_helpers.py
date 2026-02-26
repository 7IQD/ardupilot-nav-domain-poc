import numpy as np
import pandas as pd

def normalize_inverse(values, worst, best):
    """
    Lower is better (e.g., variance, HDOP)
    Works with scalar, pandas Series, or NumPy arrays
    Returns values clipped between 0–100
    """
    values = np.array(values, dtype=float)
    score = 100 * (worst - values) / (worst - best)
    return np.clip(score, 0, 100)

def normalize_direct(values, worst, best):
    """
    Higher is better (e.g., satellite count)
    Works with scalar, pandas Series, or NumPy arrays
    Returns values clipped between 0–100
    """
    values = np.array(values, dtype=float)
    score = 100 * (values - worst) / (best - worst)
    return np.clip(score, 0, 100)
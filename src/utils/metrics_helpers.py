# src/scorecards/utils/metrics_helpers.py

def normalize_inverse(value, worst, best):
    """
    Lower is better (e.g., variance, HDOP).
    Returns score 0–100.
    """
    if value >= worst:
        return 0
    if value <= best:
        return 100
    return 100 * (worst - value) / (worst - best)


def normalize_direct(value, worst, best):
    """
    Higher is better (e.g., satellite count).
    """
    if value <= worst:
        return 0
    if value >= best:
        return 100
    return 100 * (value - worst) / (best - worst)

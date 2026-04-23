def calculate_kelly(win_rate: float, reward_risk_ratio: float,
                    kelly_fraction: float = 0.5, max_pct: float = 0.20) -> float:
    """
    Returns the fraction of the swing portfolio to allocate to one position.
    Uses Half Kelly with a cap at max_pct.
    """
    p = win_rate
    q = 1.0 - win_rate
    b = reward_risk_ratio

    kelly_full = (p * b - q) / b
    kelly_sized = kelly_full * kelly_fraction

    return min(max(kelly_sized, 0.0), max_pct)

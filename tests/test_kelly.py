from kelly import calculate_kelly

def test_basic_kelly():
    # win_rate=0.55, reward_risk=2.0 → full kelly = (0.55*2 - 0.45)/2 = 0.325
    # half kelly = 0.1625, below max 0.20 → result = 0.1625
    result = calculate_kelly(win_rate=0.55, reward_risk_ratio=2.0)
    assert abs(result - 0.1625) < 0.001

def test_kelly_capped_at_max():
    # Extremely good odds that would exceed max_pct
    result = calculate_kelly(win_rate=0.95, reward_risk_ratio=5.0, max_pct=0.20)
    assert result == 0.20

def test_kelly_negative_edge_returns_zero():
    # win_rate too low → kelly is negative → return 0
    result = calculate_kelly(win_rate=0.20, reward_risk_ratio=1.0)
    assert result == 0.0

def test_kelly_as_percentage():
    result = calculate_kelly(win_rate=0.55, reward_risk_ratio=2.0)
    assert 0.0 <= result <= 0.20

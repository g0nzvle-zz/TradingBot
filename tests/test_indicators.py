import pandas as pd
import numpy as np
from indicators import calculate_indicators

def make_fake_ohlcv(n=60):
    """Create a fake OHLCV DataFrame with enough rows for all indicators."""
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=n, freq="D")
    close_values = np.linspace(100, 120, n) + np.random.normal(0, 1, n)
    volume_values = np.random.randint(1_000_000, 5_000_000, n).astype(float)
    df = pd.DataFrame({
        "Open": close_values * 0.99,
        "High": close_values * 1.01,
        "Low": close_values * 0.98,
        "Close": close_values,
        "Volume": volume_values,
    }, index=dates)
    return df

def test_calculate_indicators_returns_dict():
    df = make_fake_ohlcv()
    result = calculate_indicators(df)
    assert isinstance(result, dict)

def test_all_required_keys_present():
    df = make_fake_ohlcv()
    result = calculate_indicators(df)
    required = ["price", "rsi", "macd", "macd_signal", "macd_hist",
                "bb_upper", "bb_lower", "bb_mid", "ema20", "ema50",
                "volume", "volume_sma20"]
    for key in required:
        assert key in result, f"Missing key: {key}"

def test_rsi_in_valid_range():
    df = make_fake_ohlcv()
    result = calculate_indicators(df)
    if result["rsi"] is not None:
        assert 0 <= result["rsi"] <= 100

def test_price_is_last_close():
    df = make_fake_ohlcv()
    result = calculate_indicators(df)
    assert abs(result["price"] - float(df["Close"].iloc[-1])) < 0.01

def test_no_nan_values_in_output():
    import math
    df = make_fake_ohlcv(n=30)  # short data, may produce NaN in some indicators
    result = calculate_indicators(df)
    for key, value in result.items():
        if value is not None:
            assert not math.isnan(value), f"Key '{key}' returned NaN instead of None"

from screener import score_stock

def make_ind(rsi=50, macd=1.0, macd_signal=0.5, macd_hist=0.5,
             ema20=105.0, ema50=100.0, volume=2_000_000,
             volume_sma20=1_500_000, price=45.0,
             bb_mid=50.0, bb_lower=44.0, bb_upper=56.0):
    return {
        "rsi": rsi, "macd": macd, "macd_signal": macd_signal,
        "macd_hist": macd_hist, "ema20": ema20, "ema50": ema50,
        "volume": volume, "volume_sma20": volume_sma20, "price": price,
        "bb_mid": bb_mid, "bb_lower": bb_lower, "bb_upper": bb_upper,
    }

def test_perfect_score_is_100():
    ind = make_ind()  # all signals aligned
    assert score_stock(ind) == 100

def test_zero_score_for_bad_signals():
    ind = make_ind(rsi=80, macd=-1.0, macd_signal=0.5, macd_hist=-0.5,
                   ema20=95.0, ema50=100.0, volume=500_000,
                   volume_sma20=2_000_000, price=60.0, bb_mid=48.0)
    assert score_stock(ind) == 0

def test_score_between_0_and_100():
    ind = make_ind(rsi=50, macd_hist=-0.1, ema20=99.0, ema50=100.0)
    result = score_stock(ind)
    assert 0 <= result <= 100

def test_none_indicators_do_not_crash():
    ind = make_ind()
    ind["rsi"] = None
    ind["macd_hist"] = None
    result = score_stock(ind)
    assert isinstance(result, int)

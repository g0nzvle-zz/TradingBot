import yfinance as yf
import pandas as pd
import ta
from typing import Optional


def fetch_ohlcv(ticker: str, period: str = "3mo", interval: str = "1d") -> Optional[pd.DataFrame]:
    """Download OHLCV data for a single ticker. Returns None on failure."""
    try:
        df = yf.download(ticker, period=period, interval=interval,
                         progress=False, auto_adjust=True)
        if df.empty or len(df) < 30:
            return None
        # yfinance sometimes returns MultiIndex columns — flatten them
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception:
        return None


def calculate_indicators(df: pd.DataFrame) -> dict:
    """
    Calculate technical indicators from an OHLCV DataFrame.
    Returns a dict with all indicator values. None means calculation failed.
    """
    close = df["Close"].squeeze()
    volume = df["Volume"].squeeze()

    # RSI
    try:
        rsi_s = ta.momentum.RSIIndicator(close, window=14).rsi()
        rsi = float(rsi_s.iloc[-1]) if not rsi_s.empty else None
    except Exception:
        rsi = None

    # MACD
    try:
        macd_ind = ta.trend.MACD(close, window_slow=26, window_fast=12, window_sign=9)
        macd = float(macd_ind.macd().iloc[-1])
        macd_signal = float(macd_ind.macd_signal().iloc[-1])
        macd_hist = float(macd_ind.macd_diff().iloc[-1])
    except Exception:
        macd = macd_signal = macd_hist = None

    # Bollinger Bands
    try:
        bb = ta.volatility.BollingerBands(close, window=20, window_dev=2)
        bb_upper = float(bb.bollinger_hband().iloc[-1])
        bb_mid = float(bb.bollinger_mavg().iloc[-1])
        bb_lower = float(bb.bollinger_lband().iloc[-1])
    except Exception:
        bb_upper = bb_mid = bb_lower = None

    # EMAs
    try:
        ema20 = float(ta.trend.EMAIndicator(close, window=20).ema_indicator().iloc[-1])
    except Exception:
        ema20 = None
    try:
        ema50 = float(ta.trend.EMAIndicator(close, window=50).ema_indicator().iloc[-1])
    except Exception:
        ema50 = None

    # Volume SMA 20
    try:
        vol_sma = volume.rolling(20).mean()
        volume_sma20 = float(vol_sma.iloc[-1])
    except Exception:
        volume_sma20 = None

    return {
        "price": float(close.iloc[-1]),
        "rsi": rsi,
        "macd": macd,
        "macd_signal": macd_signal,
        "macd_hist": macd_hist,
        "bb_upper": bb_upper,
        "bb_lower": bb_lower,
        "bb_mid": bb_mid,
        "ema20": ema20,
        "ema50": ema50,
        "volume": float(volume.iloc[-1]),
        "volume_sma20": volume_sma20,
    }

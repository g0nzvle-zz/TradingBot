import os

# --- API Keys (loaded from environment variables / GitHub Secrets) ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = "TradingBot/1.0 by FelipeGonzalez"

# --- Watchlist ---
LONG_TERM_TICKERS = ["SPY", "QQQ", "VTI", "SCHD", "VWO"]

SWING_UNIVERSE = [
    "AAPL", "MSFT", "NVDA", "TSLA", "AMZN",
    "META", "GOOGL", "JPM", "AMD", "PLTR",
    "NFLX", "CRM", "ADBE", "INTC",
    "DIS", "BA", "GS", "V", "MA",
    "JNJ", "PFE", "UNH", "MRK", "ABBV",
    "XOM", "CVX", "COP",
    "WMT", "COST", "HD",
    "CAT", "GE", "HON",
    "T", "VZ", "CMCSA",
    "WFC", "BAC", "C", "MS",
    "COIN", "SHOP", "SQ", "PYPL",
]

SUBREDDITS = ["stocks", "investing", "wallstreetbets", "StockMarket"]

RSS_FEEDS = [
    "https://feeds.reuters.com/reuters/businessNews",
    "https://feeds.marketwatch.com/marketwatch/topstories/",
]

# --- Kelly Criterion parameters ---
KELLY_FRACTION = 0.5
MAX_POSITION_PCT = 0.20
SWING_WIN_RATE = 0.55
SWING_REWARD_RISK = 2.0
STOP_LOSS_PCT = 0.07

# --- Screener filters ---
MIN_PRICE = 10.0
RSI_MIN = 30
RSI_MAX = 70
TOP_N_STOCKS = 5

# --- Groq ---
GROQ_MODEL = "llama-3.3-70b-versatile"

# --- Tracker ---
TRACKER_FILE = "recommendations.csv"

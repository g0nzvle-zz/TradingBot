import os
import csv
import pytest
from unittest.mock import patch
from tracker import log_recommendations, get_previous_results

def test_log_creates_csv(tmp_path):
    csv_path = str(tmp_path / "recs.csv")
    recs = [{"ticker": "NVDA", "price": 875.0, "kelly_pct": 8.0}]
    with patch("tracker.TRACKER_FILE", csv_path):
        log_recommendations(recs)
    assert os.path.exists(csv_path)

def test_log_writes_correct_ticker(tmp_path):
    csv_path = str(tmp_path / "recs.csv")
    recs = [{"ticker": "AAPL", "price": 200.0, "kelly_pct": 5.0}]
    with patch("tracker.TRACKER_FILE", csv_path):
        log_recommendations(recs)
    with open(csv_path) as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["ticker"] == "AAPL"

def test_get_previous_results_returns_empty_if_no_file(tmp_path):
    csv_path = str(tmp_path / "nonexistent.csv")
    with patch("tracker.TRACKER_FILE", csv_path):
        result = get_previous_results()
    assert result == []

def test_get_previous_results_skips_empty_resultado(tmp_path):
    csv_path = str(tmp_path / "recs.csv")
    recs = [{"ticker": "MSFT", "price": 415.0, "kelly_pct": 5.0}]
    with patch("tracker.TRACKER_FILE", csv_path):
        log_recommendations(recs)
        # Entry has no resultado_pct yet — should not be returned if yfinance fails
        with patch("yfinance.Ticker") as mock_ticker:
            mock_ticker.side_effect = Exception("No internet")
            results = get_previous_results()
    assert results == []

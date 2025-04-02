import pytest
from openstoxlify import fetch, MarketData


def test_fetch():
    market_data = fetch("BTCUSDT", "Binance", "30m", "1mo")
    assert isinstance(market_data, MarketData)

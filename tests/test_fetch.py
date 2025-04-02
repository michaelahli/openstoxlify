import pytest
from stoxlify import fetch, MarketData


def test_fetch():
    market_data = fetch("BTC-USD", "Binance", "30m", "1mo")
    assert isinstance(market_data, MarketData)

import requests
import json

from datetime import datetime
from .models import Quote, MarketData

CANDLESTICK_DATA = []


def fetch(ticker: str, provider: str, interval: str, range_: str) -> MarketData:
    """
    Fetch market data from Stoxlify API.
    """
    url = "https://api.app.stoxlify.com/v1/market/info"
    headers = {"Content-Type": "application/json"}
    payload = {
        "ticker": ticker,
        "range": range_,
        "source": provider,
        "interval": interval,
        "indicator": "quote",
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    data = response.json()

    quotes = [
        Quote(
            timestamp=datetime.fromisoformat(q["timestamp"].replace("Z", "+00:00")),
            high=q["product_info"]["price"]["high"],
            low=q["product_info"]["price"]["low"],
            open=q["product_info"]["price"]["open"],
            close=q["product_info"]["price"]["close"],
        )
        for q in data["quote"]
    ]

    CANDLESTICK_DATA.clear()
    for quote in quotes:
        CANDLESTICK_DATA.append(
            {
                "timestamp": quote.timestamp,
                "open": quote.open,
                "high": quote.high,
                "low": quote.low,
                "close": quote.close,
            }
        )

    return MarketData(ticker=ticker, quotes=quotes)

import requests
import json

from datetime import datetime

from .models import Quote, MarketData

CANDLESTICK_DATA = []


def fetch(ticker: str, provider: str, interval: str, range_: str) -> MarketData:
    """
    Fetch market data from Stoxlify API and safely handle missing price data.
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

    quotes = []
    for q in data.get("quote", []):
        try:
            ts = datetime.fromisoformat(q["timestamp"].replace("Z", "+00:00"))
            price = q["product_info"]["price"]

            if not all(k in price for k in ("open", "high", "low", "close")):
                continue

            quote = Quote(
                timestamp=ts,
                high=price["high"],
                low=price["low"],
                open=price["open"],
                close=price["close"],
            )
            quotes.append(quote)

        except (KeyError, TypeError, ValueError):
            continue

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

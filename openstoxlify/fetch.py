import requests
import json

from datetime import datetime

from .models import Period, Provider, Quote, MarketData

CANDLESTICK_DATA = []

PERIOD_MAPPING = {
    Period.DAILY: {"interval": "1d", "range": "1y"},
    Period.WEEKLY: {"interval": "1wk", "range": "10y"},
    Period.MONTHLY: {"interval": "1mo", "range": "max"},
}


def fetch(ticker: str, provider: Provider, period: Period) -> MarketData:
    """
    Fetch market data from Stoxlify API and safely handle missing price data.
    """
    if period not in PERIOD_MAPPING:
        raise ValueError(
            f"Invalid period '{period}'. Expected one of {list(PERIOD_MAPPING.keys())}."
        )

    interval = PERIOD_MAPPING[period]["interval"]
    time_range = PERIOD_MAPPING[period]["range"]

    url = "https://api.app.stoxlify.com/v1/market/info"
    headers = {"Content-Type": "application/json"}
    payload = {
        "ticker": ticker,
        "range": time_range,
        "source": provider.value,
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

import requests
import json

from datetime import datetime

from .models import Period, Provider, Quote, MarketData

MARKET_DATA: MarketData = MarketData(
    ticker="", period=Period.DAILY, provider=Provider.YFinance, quotes=[]
)

PERIOD_MAPPING = {
    Period.DAILY: {"interval": "1d", "range": "1y"},
    Period.WEEKLY: {"interval": "1wk", "range": "10y"},
    Period.MONTHLY: {"interval": "1mo", "range": "max"},
}


def fetch(ticker: str, provider: Provider, period: Period) -> MarketData:
    """
    Fetch market data from Stoxlify API and safely handle missing price data.
    """
    global MARKET_DATA
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
                volume=price["volume"],
            )
            quotes.append(quote)

        except (KeyError, TypeError, ValueError):
            continue

    MARKET_DATA.ticker = ticker
    MARKET_DATA.period = period
    MARKET_DATA.provider = provider
    MARKET_DATA.quotes = quotes

    return MARKET_DATA

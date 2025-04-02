import requests
import json
from dataclasses import dataclass
from datetime import datetime


def fetch(ticker: str, provider: str, interval: str, range_: str) -> "MarketData":
    """
    Fetch market data from Stoxlify API.

    :param ticker: The asset ticker (e.g., BTC-USD)
    :param provider: The data provider (e.g., Binance, YFinance)
    :param interval: The time interval (e.g., 30m, 1h, 1d)
    :param range_: The range of data (e.g., 1mo, 1y)
    :return: MarketData object containing quotes
    """
    url = "https://api.france.stoxlify.com/v1/market/info"
    headers = {"Content-Type": "application/json", "Accept": "*/*"}
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

    return MarketData(ticker=ticker, quotes=quotes)


@dataclass
class Quote:
    timestamp: datetime
    high: float
    low: float
    open: float
    close: float


@dataclass
class MarketData:
    ticker: str
    quotes: list[Quote]


# Example usage
if __name__ == "__main__":
    market_data = fetch("BTC-USD", "Binance", "30m", "1mo")
    print(market_data)

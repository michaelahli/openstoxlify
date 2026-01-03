# pyright: reportAttributeAccessIssue=false
from datetime import timezone
from .proto import client
from .proto.market import market_pb2, market_pb2_grpc

from .models import Period, Provider, Quote, MarketData

MARKET_DATA: MarketData = MarketData(
    ticker="", period=Period.DAILY, provider=Provider.YFinance, quotes=[]
)

PERIOD_MAPPING = {
    Period.MINUTELY: {"interval": "1m", "range": "1wk"},
    Period.QUINTLY: {"interval": "5m", "range": "1wk"},
    Period.HALFHOURLY: {"interval": "30m", "range": "1wk"},
    Period.HOURLY: {"interval": "60m", "range": "1wk"},
    Period.DAILY: {"interval": "1d", "range": "1y"},
    Period.WEEKLY: {"interval": "1wk", "range": "10y"},
    Period.MONTHLY: {"interval": "1mo", "range": "max"},
}


def fetch(
    ticker: str,
    provider: Provider,
    period: Period,
) -> MarketData:
    global MARKET_DATA

    if period not in PERIOD_MAPPING:
        raise ValueError(
            f"Invalid period '{period}'. Expected one of {list(PERIOD_MAPPING.keys())}."
        )

    interval = PERIOD_MAPPING[period]["interval"]
    time_range = PERIOD_MAPPING[period]["range"]

    try:
        c = client.channel()
        stub = market_pb2_grpc.MarketServiceStub(c)
        req = market_pb2.GetProductInfoRequest(
            Ticker=ticker,
            Range=time_range,
            Interval=interval,
            Indicator="quote",
            Source=provider.value,
        )
        response = stub.GetProductInfo(req)
    except Exception as err:
        raise RuntimeError(f"request failed: {err}") from err

    quotes = []

    for q in response.Quote:
        ts = q.Timestamp.ToDatetime().replace(tzinfo=timezone.utc)
        price = q.ProductInfo.Price

        quotes.append(
            Quote(
                timestamp=ts,
                high=price.High,
                low=price.Low,
                open=price.Open,
                close=price.Close,
                volume=price.Volume,
            )
        )

    MARKET_DATA.ticker = ticker
    MARKET_DATA.period = period
    MARKET_DATA.provider = provider
    MARKET_DATA.quotes = quotes

    return MARKET_DATA

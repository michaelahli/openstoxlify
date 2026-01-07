import sys
import warnings

warnings.filterwarnings("ignore")

from openstoxlify.draw import Canvas
from openstoxlify.context import Context
from openstoxlify.models.enum import ActionType, DefaultProvider, Period, PlotType
from openstoxlify.models.series import ActionSeries, FloatSeries
from openstoxlify.providers.stoxlify.provider import Provider
from openstoxlify.utils.token import fetch_token

token = fetch_token(sys.argv)

provider = Provider(DefaultProvider.Binance)

ctx = Context(sys.argv, provider, "PEPEUSDT", Period.MINUTELY)
amt = 500000
market_data = ctx.quotes()

for quote in market_data:
    ctx.plot("Price", PlotType.LINE, FloatSeries(quote.timestamp, quote.close))

for quote in market_data:
    minute = quote.timestamp.minute
    if minute % 2 == 0:
        ctx.signal(ActionSeries(quote.timestamp, ActionType.LONG, amt))
    else:
        ctx.signal(ActionSeries(quote.timestamp, ActionType.SHORT, amt * 0.999))

ctx.authenticate()
ctx.execute()

c = Canvas(ctx)
c.draw()

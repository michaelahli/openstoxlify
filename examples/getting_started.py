from statistics import median

from openstoxlify.context import Context
from openstoxlify.draw import Canvas
from openstoxlify.models.enum import ActionType, DefaultProvider, Period, PlotType
from openstoxlify.models.series import ActionSeries, FloatSeries
from openstoxlify.providers.stoxlify.provider import Provider as StoxlifyProvider

provider = StoxlifyProvider(DefaultProvider.YFinance)

ctx = Context(provider, "BTC-USD", Period.DAILY)

quotes = ctx.quotes()

prices = [quote.close for quote in quotes]
median_value = median(prices)

lowest = min(quotes, key=lambda q: q.close)
highest = max(quotes, key=lambda q: q.close)

for quote in quotes:
    ctx.plot("Median", PlotType.LINE, FloatSeries(quote.timestamp, median_value))

ctx.signal(ActionSeries(lowest.timestamp, ActionType.LONG, 1))
ctx.signal(ActionSeries(highest.timestamp, ActionType.SHORT, 1))

canvas = Canvas(ctx)
canvas.draw()

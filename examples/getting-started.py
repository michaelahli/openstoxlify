from statistics import median
from openstoxlify.models import Period, Provider, PlotType, ActionType
from openstoxlify.fetch import fetch
from openstoxlify.plotter import plot
from openstoxlify.strategy import act
from openstoxlify.draw import draw

market_data = fetch("BTCUSDT", Provider.Binance, Period.MINUTELY)
quotes = market_data.quotes

prices = [quote.close for quote in quotes]
median_value = median(prices)

lowest = min(quotes, key=lambda q: q.close)
highest = max(quotes, key=lambda q: q.close)

for quote in quotes:
    plot(PlotType.LINE, "Median", quote.timestamp, median_value)

act(ActionType.LONG, lowest.timestamp, 1)
act(ActionType.SHORT, highest.timestamp, 1)

draw()

from datetime import datetime
from openstoxlify.models import MarketData, Period, PlotType, Provider
from openstoxlify.plotter import plot
from openstoxlify.fetch import fetch
from openstoxlify.draw import draw


def fetch_market_data(symbol: str) -> MarketData:
    return fetch(symbol, Provider.YFinance, Period.DAILY)


def calculate_pivot_levels(
    market_data: MarketData,
) -> list[tuple[datetime, float, float, float]]:
    levels = []
    for quote in market_data.quotes:
        high = quote.high
        low = quote.low
        close = quote.close
        timestamp = quote.timestamp

        pivot = (high + low + close) / 3
        r1 = 2 * pivot - low
        s1 = 2 * pivot - high

        levels.append((timestamp, pivot, r1, s1))

    return levels


def plot_pivot_levels(levels: list[tuple[datetime, float, float, float]]):
    for timestamp, pivot, r1, s1 in levels:
        plot(PlotType.LINE, "Pivot", timestamp, pivot)
        plot(PlotType.LINE, "Resistance 1", timestamp, r1)
        plot(PlotType.LINE, "Support 1", timestamp, s1)


market_data = fetch_market_data("BTC-USD")
pivot_levels = calculate_pivot_levels(market_data)
plot_pivot_levels(pivot_levels)
draw()

from datetime import datetime
from statistics import mean, stdev

from openstoxlify.models import MarketData, Period, PlotType, ActionType, Provider
from openstoxlify.plotter import plot
from openstoxlify.fetch import fetch
from openstoxlify.draw import draw
from openstoxlify.strategy import act


def fetch_market_data(symbol: str) -> MarketData:
    return fetch(symbol, Provider.YFinance, Period.DAILY)


def calculate_bollinger_bands(market_data: MarketData, window: int = 20):
    quotes = market_data.quotes
    bands = []

    for i in range(len(quotes) - window + 1):
        window_quotes = quotes[i : i + window]
        closes = [q.close for q in window_quotes]
        sma = mean(closes)
        sd = stdev(closes)

        timestamp = window_quotes[-1].timestamp
        upper = sma + 2 * sd
        lower = sma - 2 * sd

        bands.append((timestamp, sma, upper, lower))

    return bands


def plot_bollinger_bands(bands: list[tuple[datetime, float, float, float]]):
    for timestamp, sma, upper, lower in bands:
        plot(PlotType.LINE, "SMA", timestamp, sma)
        plot(PlotType.AREA, "BB Upper", timestamp, upper)
        plot(PlotType.AREA, "BB Lower", timestamp, lower)


def generate_bb_strategy_signals(market_data: MarketData, bands):
    price_map = {q.timestamp: q.close for q in market_data.quotes}
    last_action = ActionType.HOLD

    for timestamp, sma, upper, lower in bands:
        price = price_map.get(timestamp)
        if price is None:
            continue

        if price > upper and last_action != ActionType.SHORT:
            act(ActionType.SHORT, timestamp, 1000)
            last_action = ActionType.SHORT
        elif price < lower and last_action != ActionType.LONG:
            act(ActionType.LONG, timestamp, 1000)
            last_action = ActionType.LONG


market_data = fetch_market_data("BTC-USD")
bands = calculate_bollinger_bands(market_data)

plot_bollinger_bands(bands)
generate_bb_strategy_signals(market_data, bands)

draw()

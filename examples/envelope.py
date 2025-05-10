from datetime import datetime

from openstoxlify.models import MarketData, Period, PlotType, ActionType, Provider
from openstoxlify.plotter import plot
from openstoxlify.fetch import fetch
from openstoxlify.draw import draw
from openstoxlify.strategy import act


def fetch_market_data(symbol: str) -> MarketData:
    return fetch(symbol, Provider.YFinance, Period.DAILY)


def calculate_sma(market_data: MarketData, window: int) -> list[tuple[datetime, float]]:
    prices = [quote.close for quote in market_data.quotes]
    return [
        (
            market_data.quotes[i + window - 1].timestamp,
            sum(prices[i : i + window]) / window,
        )
        for i in range(len(prices) - window + 1)
    ]


def calculate_envelope(
    sma_values: list[tuple[datetime, float]],
    percentage: float,
) -> tuple[list[tuple[datetime, float]], list[tuple[datetime, float]]]:
    upper = [(ts, val * (1 + percentage)) for ts, val in sma_values]
    lower = [(ts, val * (1 - percentage)) for ts, val in sma_values]
    return upper, lower


def plot_envelope(
    sma: list[tuple[datetime, float]],
    upper: list[tuple[datetime, float]],
    lower: list[tuple[datetime, float]],
):
    for ts, val in sma:
        plot(PlotType.LINE, "SMA", ts, val)
    for ts, val in upper:
        plot(PlotType.LINE, "Envelope Upper", ts, val)
    for ts, val in lower:
        plot(PlotType.LINE, "Envelope Lower", ts, val)


def generate_envelope_strategy(
    market_data: MarketData,
    lower: list[tuple[datetime, float]],
    upper: list[tuple[datetime, float]],
):
    lower_dict = dict(lower)
    upper_dict = dict(upper)
    last_action = ActionType.HOLD
    for quote in market_data.quotes:
        if quote.timestamp not in lower_dict or quote.timestamp not in upper_dict:
            continue
        if quote.close < lower_dict[quote.timestamp] and last_action != ActionType.LONG:
            act(ActionType.LONG, quote.timestamp, 1)
            last_action = ActionType.LONG
        elif (
            quote.close > upper_dict[quote.timestamp]
            and last_action != ActionType.SHORT
        ):
            act(ActionType.SHORT, quote.timestamp, 1)
            last_action = ActionType.SHORT


market_data = fetch_market_data("BTC-USD")

sma = calculate_sma(market_data, window=20)
upper, lower = calculate_envelope(sma, percentage=0.02)

plot_envelope(sma, upper, lower)
generate_envelope_strategy(market_data, lower, upper)

draw()

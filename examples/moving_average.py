from datetime import datetime

from openstoxlify.models import MarketData, PlotType, ActionType
from openstoxlify.plotter import plot
from openstoxlify.fetch import fetch
from openstoxlify.draw import draw
from openstoxlify.strategy import act


def fetch_market_data(symbol: str) -> MarketData:
    return fetch(symbol, "YFinance", "1d", "6mo")


def calculate_sma(market_data: MarketData, window: int) -> list[tuple[datetime, float]]:
    prices = [quote.close for quote in market_data.quotes]

    if len(prices) < window:
        raise ValueError("Not enough data points to compute SMA.")

    return [
        (
            market_data.quotes[i + window - 1].timestamp,
            sum(prices[i : i + window]) / window,
        )
        for i in range(len(prices) - window + 1)
    ]


def plot_sma(sma_values: list[tuple[datetime, float]], label: str):
    for timestamp, value in sma_values:
        plot(PlotType.LINE, label, timestamp, value)


def generate_strategy_signals(
    sma_fast: list[tuple[datetime, float]],
    sma_slow: list[tuple[datetime, float]],
):
    slow_dict = dict(sma_slow)
    last_action = ActionType.HOLD

    for timestamp, fast_value in sma_fast:
        slow_value = slow_dict.get(timestamp)
        if slow_value is None:
            continue

        if fast_value > slow_value and last_action != ActionType.LONG:
            act(ActionType.LONG, timestamp)
            last_action = ActionType.LONG
        elif fast_value < slow_value and last_action != ActionType.SHORT:
            act(ActionType.SHORT, timestamp)
            last_action = ActionType.SHORT
        else:
            act(ActionType.HOLD, timestamp)


market_data = fetch_market_data("BTC-USD")

sma_9 = calculate_sma(market_data, window=9)
sma_14 = calculate_sma(market_data, window=14)
sma_50 = calculate_sma(market_data, window=50)

plot_sma(sma_9, label="SMA 9")
plot_sma(sma_14, label="SMA 14")
plot_sma(sma_50, label="SMA 50")

generate_strategy_signals(sma_14, sma_50)
draw()

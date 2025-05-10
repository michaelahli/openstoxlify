from datetime import datetime
import statistics
from openstoxlify.models import MarketData, Period, PlotType, ActionType, Provider
from openstoxlify.plotter import plot
from openstoxlify.fetch import fetch
from openstoxlify.draw import draw
from openstoxlify.strategy import act


def fetch_market_data(symbol: str) -> MarketData:
    return fetch(symbol, Provider.YFinance, Period.DAILY)


def calculate_bollinger_bands(market_data: MarketData, window: int = 20):
    prices = [quote.close for quote in market_data.quotes]
    timestamps = [quote.timestamp for quote in market_data.quotes]

    middle = []
    upper = []
    lower = []

    for i in range(len(prices) - window + 1):
        window_prices = prices[i : i + window]
        sma = sum(window_prices) / window
        std = statistics.stdev(window_prices)

        timestamp = timestamps[i + window - 1]
        middle.append((timestamp, sma))
        upper.append((timestamp, sma + 2 * std))
        lower.append((timestamp, sma - 2 * std))

    return middle, upper, lower


def plot_bands(middle, upper, lower):
    for timestamp, value in middle:
        plot(PlotType.LINE, "BB Middle", timestamp, value)
    for timestamp, value in upper:
        plot(PlotType.LINE, "BB Upper", timestamp, value)
    for timestamp, value in lower:
        plot(PlotType.LINE, "BB Lower", timestamp, value)


def generate_signals(market_data, middle, upper, lower):
    band_dict = {
        ts: (mid, up, low) for (ts, mid), (_, up), (_, low) in zip(middle, upper, lower)
    }
    last_action = ActionType.HOLD

    for quote in market_data.quotes[19:]:
        if quote.timestamp not in band_dict:
            continue

        mid, up, low = band_dict[quote.timestamp]

        if quote.close <= low and last_action != ActionType.LONG:
            act(ActionType.LONG, quote.timestamp, 1)
            last_action = ActionType.LONG
        elif quote.close >= up and last_action != ActionType.SHORT:
            act(ActionType.SHORT, quote.timestamp, 1)
            last_action = ActionType.SHORT


market_data = fetch_market_data("BTC-USD")
middle_band, upper_band, lower_band = calculate_bollinger_bands(market_data)
plot_bands(middle_band, upper_band, lower_band)
generate_signals(market_data, middle_band, upper_band, lower_band)
draw()

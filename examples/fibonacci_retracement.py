from datetime import datetime, timedelta
from openstoxlify.models import MarketData, Period, PlotType, ActionType, Provider
from openstoxlify.plotter import plot
from openstoxlify.fetch import fetch
from openstoxlify.draw import draw
from openstoxlify.strategy import act


def fetch_market_data(symbol: str) -> MarketData:
    return fetch(symbol, Provider.YFinance, Period.DAILY)


def calculate_repeating_fib_levels(market_data: MarketData, lookback_days=90):
    quotes = market_data.quotes
    if not quotes:
        return []

    start_date = quotes[0].timestamp
    end_date = quotes[-1].timestamp
    current_start = start_date
    fib_windows = []

    while current_start < end_date:
        current_end = current_start + timedelta(days=lookback_days)
        window_quotes = [
            q for q in quotes if current_start <= q.timestamp < current_end
        ]

        if window_quotes:
            high = max(q.high for q in window_quotes)
            low = min(q.low for q in window_quotes)
            diff = high - low

            levels = {
                "0%": high,
                "23.6%": high - diff * 0.236,
                "38.2%": high - diff * 0.382,
                "50%": high - diff * 0.5,
                "61.8%": high - diff * 0.618,
                "100%": low,
            }
            fib_windows.append((current_start, current_end, levels))

        current_start = current_end

    return fib_windows


def plot_repeating_fib_levels(fib_windows):
    for start_ts, end_ts, levels in fib_windows:
        for name, level in levels.items():
            plot(PlotType.LINE, f"Fib {name}", start_ts, level)
            plot(PlotType.LINE, f"Fib {name}", end_ts, level)


def generate_signals(market_data, fib_windows):
    last_quote = market_data.quotes[-1]
    current_window = None

    for start_ts, end_ts, levels in fib_windows:
        if start_ts <= last_quote.timestamp <= end_ts:
            current_window = levels
            break

    if current_window:
        if (
            last_quote.close <= current_window["61.8%"]
            and last_quote.close > current_window["100%"]
        ):
            act(ActionType.LONG, last_quote.timestamp, 1)
        elif (
            last_quote.close >= current_window["38.2%"]
            and last_quote.close < current_window["0%"]
        ):
            act(ActionType.SHORT, last_quote.timestamp, 1)


market_data = fetch_market_data("BTC-USD")
fib_windows = calculate_repeating_fib_levels(market_data, lookback_days=30)
plot_repeating_fib_levels(fib_windows)
generate_signals(market_data, fib_windows)
draw()

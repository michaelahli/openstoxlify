from datetime import datetime, timedelta
from openstoxlify.draw import draw
from openstoxlify.models import MarketData, Period, PlotType, ActionType, Provider
from openstoxlify.plotter import plot
from openstoxlify.fetch import fetch
from openstoxlify.strategy import act


def fetch_market_data(symbol: str) -> MarketData:
    return fetch(symbol, Provider.YFinance, Period.DAILY)


def calculate_fib_levels(quotes, start_idx, end_idx):
    window_quotes = quotes[start_idx : end_idx + 1]
    high = max(q.high for q in window_quotes)
    low = min(q.low for q in window_quotes)
    diff = high - low

    return {
        "100%": high,
        "78.6": high - diff * 0.236,
        "61.8%": high - diff * 0.382,
        "50%": high - diff * 0.5,
        "38.2%": high - diff * 0.618,
        "23.6%": high - diff * 0.786,
        "0%": low,
    }


def get_rolling_fib_windows(market_data, lookback_days=90):
    quotes = market_data.quotes
    if not quotes:
        return []

    fib_windows = []
    current_start = 0
    current_levels = calculate_fib_levels(
        quotes, 0, min(lookback_days, len(quotes) - 1)
    )
    start_ts = quotes[0].timestamp

    for i in range(1, len(quotes)):
        current_ts = quotes[i].timestamp
        if current_ts - start_ts >= timedelta(days=lookback_days):
            if (
                quotes[i].high > current_levels["0%"]
                or quotes[i].low < current_levels["100%"]
            ):
                fib_windows.append((start_ts, current_ts, current_levels))
                current_start = i
                start_ts = current_ts
                current_levels = calculate_fib_levels(
                    quotes,
                    current_start,
                    min(current_start + lookback_days, len(quotes) - 1),
                )

    fib_windows.append((start_ts, quotes[-1].timestamp, current_levels))
    return fib_windows


def plot_fib_levels(fib_windows):
    for start_ts, end_ts, levels in fib_windows:
        for name in levels:
            plot(PlotType.LINE, f"Fib {name}", start_ts, levels[name])
            plot(PlotType.LINE, f"Fib {name}", end_ts, levels[name])


def generate_signals(market_data, fib_windows):
    if not fib_windows or not market_data.quotes:
        return

    last_action = ActionType.HOLD

    for quote in market_data.quotes:
        current_levels = None
        for start_ts, end_ts, levels in fib_windows:
            if start_ts <= quote.timestamp <= end_ts:
                current_levels = levels
                break

        if not current_levels:
            continue

        current_price = quote.close
        in_buy_zone = current_levels["0%"] <= current_price <= current_levels["38.2%"]
        in_sell_zone = (
            current_levels["61.8%"] <= current_price <= current_levels["100%"]
        )

        if in_buy_zone and last_action != ActionType.LONG:
            act(ActionType.LONG, quote.timestamp, 1)
            last_action = ActionType.LONG
        elif in_sell_zone and last_action == ActionType.LONG:
            act(ActionType.SHORT, quote.timestamp, 1)
            last_action = ActionType.SHORT


market_data = fetch_market_data("BTC-USD")
fib_windows = get_rolling_fib_windows(market_data, lookback_days=30)
plot_fib_levels(fib_windows)
generate_signals(market_data, fib_windows)
draw()

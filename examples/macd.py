from openstoxlify.models import MarketData, Period, PlotType, ActionType, Provider
from openstoxlify.plotter import plot
from openstoxlify.fetch import fetch
from openstoxlify.draw import draw
from openstoxlify.strategy import act


def fetch_market_data(symbol: str) -> MarketData:
    return fetch(symbol, Provider.YFinance, Period.DAILY)


def calculate_ema(values, period):
    ema = []
    multiplier = 2 / (period + 1)
    ema.append(sum(values[:period]) / period)
    for i in range(period, len(values)):
        ema.append((values[i] - ema[-1]) * multiplier + ema[-1])
    return ema


def calculate_macd(market_data: MarketData, fast=12, slow=26, signal=9):
    closes = [q.close for q in market_data.quotes]
    timestamps = [q.timestamp for q in market_data.quotes][slow + signal - 2 :]

    ema_fast = calculate_ema(closes, fast)[slow - fast :]
    ema_slow = calculate_ema(closes, slow)
    macd_line = [fast - slow for fast, slow in zip(ema_fast, ema_slow)]

    signal_line = calculate_ema(macd_line, signal)
    histogram = [m - s for m, s in zip(macd_line[signal - 1 :], signal_line)]

    macd_ts = [
        (timestamps[i], macd_line[signal - 1 + i])
        for i in range(len(macd_line) - signal + 1)
    ]
    signal_ts = [(timestamps[i], signal_line[i]) for i in range(len(signal_line))]
    hist_ts = [(timestamps[i], histogram[i]) for i in range(len(histogram))]

    return macd_ts, signal_ts, hist_ts


def plot_macd(macd, signal, histogram, price_min, price_max):
    scale_factor = (price_max - price_min) / 4
    offset = price_min

    for ts, val in macd:
        plot(
            PlotType.LINE,
            "MACD",
            ts,
            offset + val * scale_factor / max(1, max(abs(v) for _, v in macd)),
            1,
        )

    for ts, val in signal:
        plot(
            PlotType.LINE,
            "Signal",
            ts,
            offset + val * scale_factor / max(1, max(abs(v) for _, v in signal)),
            1,
        )

    for ts, val in histogram:
        plot(
            PlotType.HISTOGRAM,
            "Histogram",
            ts,
            offset + val * scale_factor / max(1, max(abs(v) for _, v in histogram)),
            1,
        )


def generate_signals(market_data, macd, signal):
    macd_dict = dict(macd)
    signal_dict = dict(signal)
    last_action = ActionType.HOLD

    for quote in market_data.quotes[34:]:
        if quote.timestamp not in macd_dict or quote.timestamp not in signal_dict:
            continue

        macd_val = macd_dict[quote.timestamp]
        signal_val = signal_dict[quote.timestamp]

        if macd_val > signal_val and last_action != ActionType.LONG:
            act(ActionType.LONG, quote.timestamp, 1)
            last_action = ActionType.LONG
        elif macd_val < signal_val and last_action != ActionType.SHORT:
            act(ActionType.SHORT, quote.timestamp, 1)
            last_action = ActionType.SHORT


market_data = fetch_market_data("BTC-USD")
price_min = min(q.low for q in market_data.quotes)
price_max = max(q.high for q in market_data.quotes)
macd, signal, hist = calculate_macd(market_data)
plot_macd(macd, signal, hist, price_min, price_max)
generate_signals(market_data, macd, signal)
draw()

import sys

from openstoxlify.context import Context
from openstoxlify.draw import Canvas
from openstoxlify.providers.stoxlify.provider import Provider as StoxlifyProvider

from openstoxlify.models.enum import ActionType, DefaultProvider, Period, PlotType
from openstoxlify.models.series import ActionSeries, FloatSeries

provider = StoxlifyProvider(DefaultProvider.YFinance)

ctx = Context(sys.argv, provider, "BTC-USD", Period.DAILY)

market_data = ctx.quotes()


def calculate_average(market_data, window):
    prices = [q.close for q in market_data]
    return [
        (
            market_data[i + window - 1].timestamp,
            sum(prices[i : i + window]) / window,
        )
        for i in range(len(prices) - window + 1)
    ]


def calculate_average_values(values, period):
    return [
        sum(values[i : i + period]) / period for i in range(len(values) - period + 1)
    ]


def calculate_macd(market_data, fast_period, slow_period, signal_period):
    closes = [q.close for q in market_data]
    fast = calculate_average_values(closes, fast_period)
    slow = calculate_average_values(closes, slow_period)
    macd_line = [f - s for f, s in zip(fast, slow)]
    signal_line = calculate_average_values(macd_line, signal_period)
    histogram = [m - s for m, s in zip(macd_line[-len(signal_line) :], signal_line)]
    timestamps = [
        market_data[i].timestamp
        for i in range(slow_period + signal_period - 2, len(closes))
    ]
    return [(t, h) for t, h in zip(timestamps, histogram)]


def calculate_stochastic(market_data, period):
    quotes = market_data
    highs = [q.high for q in quotes]
    lows = [q.low for q in quotes]
    closes = [q.close for q in quotes]
    results = []
    for i in range(period - 1, len(closes)):
        high_range = max(highs[i - period + 1 : i + 1])
        low_range = min(lows[i - period + 1 : i + 1])
        value = (
            100 * ((closes[i] - low_range) / (high_range - low_range))
            if high_range != low_range
            else 50
        )
        results.append((quotes[i].timestamp, value))
    return results


ma_fast = calculate_average(market_data, 20)
ma_slow = calculate_average(market_data, 50)
macd_hist = calculate_macd(market_data, 12, 26, 9)
stochastic = calculate_stochastic(market_data, 14)

for q in market_data:
    ctx.plot("Price", PlotType.LINE, FloatSeries(q.timestamp, q.close))

for t, v in ma_fast:
    ctx.plot("MA 20", PlotType.LINE, FloatSeries(t, v))

for t, v in ma_slow:
    ctx.plot("MA 50", PlotType.LINE, FloatSeries(t, v))

for t, v in macd_hist:
    ctx.plot("MACD Histogram", PlotType.HISTOGRAM, FloatSeries(t, v), 1)

for t, v in stochastic:
    ctx.plot("Stochastic", PlotType.LINE, FloatSeries(t, v), 2)

ma_fast_dict = dict(ma_fast)
ma_slow_dict = dict(ma_slow)
macd_dict = dict(macd_hist)
stoch_dict = dict(stochastic)

for q in market_data:
    ts = q.timestamp
    if (
        ts in ma_fast_dict
        and ts in ma_slow_dict
        and ts in macd_dict
        and ts in stoch_dict
    ):
        if (
            ma_fast_dict[ts] > ma_slow_dict[ts]
            and macd_dict[ts] > 0
            and stoch_dict[ts] < 20
        ):
            ctx.signal(ActionSeries(ts, ActionType.LONG, 1))
        elif (
            ma_fast_dict[ts] < ma_slow_dict[ts]
            and macd_dict[ts] < 0
            and stoch_dict[ts] > 80
        ):
            ctx.signal(ActionSeries(ts, ActionType.SHORT, 1))

canvas = Canvas(ctx)
canvas.draw()

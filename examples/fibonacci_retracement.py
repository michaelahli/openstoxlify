from openstoxlify.models import Period, Provider, PlotType, ActionType
from openstoxlify.fetch import fetch
from openstoxlify.plotter import plot
from openstoxlify.strategy import act
from openstoxlify.draw import draw
from datetime import datetime, timedelta, timezone

data = fetch("PEPEUSDT", Provider.Binance, Period.QUINTLY)
quotes = data.quotes
closes = [q.close for q in quotes]


def calculate_fibonacci_levels(data):
    max_price = max(data)
    min_price = min(data)
    diff = max_price - min_price
    return {
        "0.0": max_price,
        "0.236": max_price - 0.236 * diff,
        "0.382": max_price - 0.382 * diff,
        "0.5": max_price - 0.5 * diff,
        "0.618": max_price - 0.618 * diff,
        "0.786": max_price - 0.786 * diff,
        "1.0": min_price,
    }


def get_start_index_from_now(hours=0, days=0):
    now = datetime.now(timezone.utc)
    target_time = now - timedelta(hours=hours, days=days)
    target_time = target_time.replace(minute=0, second=0, microsecond=0)

    for idx, q in enumerate(quotes):
        q_time = q.timestamp
        if isinstance(q_time, float):
            q_time = datetime.fromtimestamp(q_time, tz=timezone.utc)
        elif q_time.tzinfo is None:
            q_time = q_time.replace(tzinfo=timezone.utc)

        if q_time >= target_time:
            return idx
    return 0


lookback = 30
current_position = None
amt = 500000
start_hour = 48

start_index = get_start_index_from_now(hours=start_hour)

fib_ranges = []
for i in range(0, len(closes), lookback):
    start = i
    end = min(i + lookback, len(closes))
    segment_closes = closes[start:end]
    if len(segment_closes) < 2:
        continue
    levels = calculate_fibonacci_levels(segment_closes)
    fib_ranges.append((start, end, levels))

for i in range(start_index, len(closes)):
    current_range = None
    current_range_idx = 0
    for idx, (start, end, levels) in enumerate(fib_ranges):
        if start <= i < end:
            current_range = (start, end, levels)
            current_range_idx = idx
            break

    if current_range is None or current_range_idx == 0:
        continue

    _, _, current_levels = current_range
    _, _, prev_levels = fib_ranges[current_range_idx - 1]

    current_time = quotes[i].timestamp
    current_price = closes[i]

    plot(PlotType.LINE, "Price", current_time, current_price)
    plot(PlotType.LINE, "Fib 0.236", current_time, current_levels["0.236"])
    plot(PlotType.LINE, "Fib 0.382", current_time, current_levels["0.382"])
    plot(PlotType.LINE, "Fib 0.5", current_time, current_levels["0.5"])
    plot(PlotType.LINE, "Fib 0.618", current_time, current_levels["0.618"])
    plot(PlotType.LINE, "Fib 0.786", current_time, current_levels["0.786"])

    # Trade decision based on previous period levels
    if (
        current_position != ActionType.LONG
        and current_price < prev_levels["0.786"]
        and current_price > prev_levels["1.0"]
    ):
        act(ActionType.LONG, current_time, amt)
        current_position = ActionType.LONG
    elif (
        current_position != ActionType.SHORT
        and current_price > prev_levels["0.236"]
        and current_price < prev_levels["0.0"]
    ):
        act(ActionType.SHORT, current_time, amt * 0.999)
        current_position = ActionType.SHORT

draw()

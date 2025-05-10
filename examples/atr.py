from datetime import datetime
from openstoxlify.models import MarketData, Period, PlotType, ActionType, Provider
from openstoxlify.plotter import plot
from openstoxlify.fetch import fetch
from openstoxlify.draw import draw
from openstoxlify.strategy import act


def fetch_market_data(symbol: str) -> MarketData:
    return fetch(symbol, Provider.YFinance, Period.DAILY)


def calculate_atr(market_data: MarketData, period=14):
    quotes = market_data.quotes
    highs = [q.high for q in quotes]
    lows = [q.low for q in quotes]
    closes = [q.close for q in quotes]
    timestamps = [q.timestamp for q in quotes]

    tr = []
    for i in range(1, len(quotes)):
        high_low = highs[i] - lows[i]
        high_close = abs(highs[i] - closes[i - 1])
        low_close = abs(lows[i] - closes[i - 1])
        tr.append(max(high_low, high_close, low_close))

    atr = []
    for i in range(period, len(tr)):
        atr_val = sum(tr[i - period : i]) / period
        atr.append((timestamps[i], atr_val))

    return atr


def calculate_price_changes(market_data):
    quotes = market_data.quotes
    price_changes = []
    for i in range(1, len(quotes)):
        change = quotes[i].close - quotes[i - 1].close
        price_changes.append((quotes[i].timestamp, change))
    return price_changes


def plot_atr_with_bounds(atr, price_changes, price_min, price_max):
    scale_factor = (price_max - price_min) / 4
    offset = price_min

    max_abs_change = max(abs(v) for _, v in price_changes) if price_changes else 1
    max_atr = max(v for _, v in atr) if atr else 1

    for ts, val in price_changes:
        scaled_val = offset + (val * scale_factor / max_abs_change)
        plot(PlotType.LINE, "Price Change", ts, scaled_val)

    for ts, val in atr:
        scaled_val = offset + (val * scale_factor / max_atr)
        plot(PlotType.LINE, "ATR", ts, scaled_val)
        plot(PlotType.LINE, "-ATR", ts, offset - (val * scale_factor / max_atr))


def generate_signals(market_data, atr):
    atr_dict = dict(atr)
    last_close = None
    last_action = ActionType.HOLD

    for quote in market_data.quotes[15:]:
        if quote.timestamp not in atr_dict:
            continue

        current_atr = atr_dict[quote.timestamp]

        if last_close is not None:
            price_change = quote.close - last_close
            if price_change > current_atr and last_action != ActionType.LONG:
                act(ActionType.LONG, quote.timestamp, 1)
                last_action = ActionType.LONG
            elif price_change < -current_atr and last_action != ActionType.SHORT:
                act(ActionType.SHORT, quote.timestamp, 1)
                last_action = ActionType.SHORT

        last_close = quote.close


market_data = fetch_market_data("BTC-USD")
price_min = min(q.low for q in market_data.quotes)
price_max = max(q.high for q in market_data.quotes)
atr = calculate_atr(market_data)
price_changes = calculate_price_changes(market_data)
plot_atr_with_bounds(atr, price_changes, price_min, price_max)
generate_signals(market_data, atr)
draw()

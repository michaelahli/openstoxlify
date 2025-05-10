from openstoxlify.models import MarketData, Period, PlotType, ActionType, Provider
from openstoxlify.plotter import plot
from openstoxlify.fetch import fetch
from openstoxlify.draw import draw
from openstoxlify.strategy import act


def fetch_market_data(symbol: str) -> MarketData:
    return fetch(symbol, Provider.YFinance, Period.DAILY)


def highest_high(quotes, start, end):
    return max(q.high for q in quotes[start:end])


def lowest_low(quotes, start, end):
    return min(q.low for q in quotes[start:end])


def calculate_ichimoku(market_data: MarketData):
    quotes = market_data.quotes
    tenkan = []
    kijun = []
    senkou_a = []
    senkou_b = []
    chikou = []

    for i in range(len(quotes)):
        if i >= 9:
            high_9 = highest_high(quotes, i - 9, i)
            low_9 = lowest_low(quotes, i - 9, i)
            tenkan.append((quotes[i].timestamp, (high_9 + low_9) / 2))
        if i >= 26:
            high_26 = highest_high(quotes, i - 26, i)
            low_26 = lowest_low(quotes, i - 26, i)
            kijun.append((quotes[i].timestamp, (high_26 + low_26) / 2))
        if i >= 52:
            high_52 = highest_high(quotes, i - 52, i)
            low_52 = lowest_low(quotes, i - 52, i)
            senkou_b.append(
                (quotes[i + 26].timestamp, (high_52 + low_52) / 2)
                if i + 26 < len(quotes)
                else None
            )
        if i >= 26 and len(tenkan) >= i - 26 + 1 and len(kijun) >= i - 26 + 1:
            a = (tenkan[i - 26][1] + kijun[i - 26][1]) / 2
            ts = quotes[i].timestamp
            if i + 26 < len(quotes):
                senkou_a.append((quotes[i + 26].timestamp, a))
        if i >= 26:
            chikou.append((quotes[i - 26].timestamp, quotes[i].close))

    senkou_b = [x for x in senkou_b if x is not None]
    return tenkan, kijun, senkou_a, senkou_b, chikou


def plot_ichimoku(tenkan, kijun, senkou_a, senkou_b, chikou):
    for ts, val in tenkan:
        plot(PlotType.LINE, "Tenkan", ts, val)
    for ts, val in kijun:
        plot(PlotType.LINE, "Kijun", ts, val)
    for ts, val in senkou_a:
        plot(PlotType.LINE, "Senkou A", ts, val)
    for ts, val in senkou_b:
        plot(PlotType.LINE, "Senkou B", ts, val)
    for ts, val in chikou:
        plot(PlotType.LINE, "Chikou", ts, val)


def generate_ichimoku_strategy(market_data: MarketData, tenkan, kijun):
    tenkan_dict = dict(tenkan)
    kijun_dict = dict(kijun)
    last_action = ActionType.HOLD
    for quote in market_data.quotes:
        ts = quote.timestamp
        if ts not in tenkan_dict or ts not in kijun_dict:
            continue
        if tenkan_dict[ts] > kijun_dict[ts] and last_action != ActionType.LONG:
            act(ActionType.LONG, ts, 1)
            last_action = ActionType.LONG
        elif tenkan_dict[ts] < kijun_dict[ts] and last_action != ActionType.SHORT:
            act(ActionType.SHORT, ts, 1)
            last_action = ActionType.SHORT


market_data = fetch_market_data("BTC-USD")

tenkan, kijun, senkou_a, senkou_b, chikou = calculate_ichimoku(market_data)
plot_ichimoku(tenkan, kijun, senkou_a, senkou_b, chikou)
generate_ichimoku_strategy(market_data, tenkan, kijun)

draw()

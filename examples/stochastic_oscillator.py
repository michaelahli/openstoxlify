from openstoxlify.models import MarketData, Period, PlotType, ActionType, Provider
from openstoxlify.plotter import plot
from openstoxlify.fetch import fetch
from openstoxlify.draw import draw
from openstoxlify.strategy import act


def fetch_market_data(symbol: str) -> MarketData:
    return fetch(symbol, Provider.YFinance, Period.DAILY)


def calculate_stochastic(market_data: MarketData, k_period=14, d_period=3):
    quotes = market_data.quotes
    timestamps = [q.timestamp for q in quotes]
    highs = [q.high for q in quotes]
    lows = [q.low for q in quotes]
    closes = [q.close for q in quotes]

    stoch_k = []
    stoch_d = []

    for i in range(k_period - 1, len(closes)):
        current_high = max(highs[i - k_period + 1 : i + 1])
        current_low = min(lows[i - k_period + 1 : i + 1])
        k = (
            100 * ((closes[i] - current_low) / (current_high - current_low))
            if current_high != current_low
            else 50
        )
        stoch_k.append((timestamps[i], k))

    for i in range(len(stoch_k) - d_period + 1):
        d = sum(val for ts, val in stoch_k[i : i + d_period]) / d_period
        stoch_d.append((stoch_k[i + d_period - 1][0], d))

    return stoch_k, stoch_d


def plot_stochastic(stoch_k, stoch_d, price_min, price_max):
    scale_factor = (price_max - price_min) / 4
    offset = price_min

    for ts, val in stoch_k:
        scaled_val = offset + (val * scale_factor / 100)
        plot(PlotType.LINE, "%K", ts, scaled_val, 1)

    for ts, val in stoch_d:
        scaled_val = offset + (val * scale_factor / 100)
        plot(PlotType.LINE, "%D", ts, scaled_val, 1)

    for ts, _ in stoch_k:
        plot(PlotType.LINE, "Overbought", ts, offset + (80 * scale_factor / 100), 1)
        plot(PlotType.LINE, "Oversold", ts, offset + (20 * scale_factor / 100), 1)


def generate_signals(market_data, stoch_k, stoch_d):
    k_dict = dict(stoch_k)
    d_dict = dict(stoch_d)
    last_action = ActionType.HOLD

    for quote in market_data.quotes[16:]:
        if quote.timestamp not in k_dict or quote.timestamp not in d_dict:
            continue

        k = k_dict[quote.timestamp]
        d = d_dict[quote.timestamp]

        if k < 20 and d < 20 and k > d and last_action != ActionType.LONG:
            act(ActionType.LONG, quote.timestamp, 1)
            last_action = ActionType.LONG
        elif k > 80 and d > 80 and k < d and last_action != ActionType.SHORT:
            act(ActionType.SHORT, quote.timestamp, 1)
            last_action = ActionType.SHORT


market_data = fetch_market_data("BTC-USD")
price_min = min(q.low for q in market_data.quotes)
price_max = max(q.high for q in market_data.quotes)
stoch_k, stoch_d = calculate_stochastic(market_data)
plot_stochastic(stoch_k, stoch_d, price_min, price_max)
generate_signals(market_data, stoch_k, stoch_d)
draw()

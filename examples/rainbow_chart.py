from openstoxlify.models import MarketData, Period, PlotType, ActionType, Provider
from openstoxlify.plotter import plot
from openstoxlify.fetch import fetch
from openstoxlify.draw import draw
from openstoxlify.strategy import act


def fetch_market_data(symbol: str) -> MarketData:
    return fetch(symbol, Provider.YFinance, Period.DAILY)


def calculate_rainbow_ma(market_data: MarketData, periods=[2, 5, 10, 20, 30, 40, 50]):
    prices = [quote.close for quote in market_data.quotes]
    timestamps = [quote.timestamp for quote in market_data.quotes]

    ma_list = []
    for period in periods:
        ma_values = []
        for i in range(len(prices) - period + 1):
            window = prices[i : i + period]
            ma_values.append((timestamps[i + period - 1], sum(window) / period))
        ma_list.append(ma_values)
    return ma_list


def plot_rainbow(ma_list, periods=[2, 5, 10, 20, 30, 40, 50]):
    colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
    for ma, period, color in zip(ma_list, periods, colors):
        for timestamp, value in ma:
            plot(PlotType.LINE, f"MA {period}", timestamp, value)


def generate_signals(market_data, ma_list):
    last_action = ActionType.HOLD
    ma_dicts = [{ts: val for ts, val in ma} for ma in ma_list]

    for quote in market_data.quotes[49:]:
        current_vals = [d.get(quote.timestamp) for d in ma_dicts]
        if None in current_vals:
            continue

        if (
            all(quote.close > val for val in current_vals)
            and last_action != ActionType.LONG
        ):
            act(ActionType.LONG, quote.timestamp, 1)
            last_action = ActionType.LONG
        elif (
            all(quote.close < val for val in current_vals)
            and last_action != ActionType.SHORT
        ):
            act(ActionType.SHORT, quote.timestamp, 1)
            last_action = ActionType.SHORT


market_data = fetch_market_data("BTC-USD")
ma_list = calculate_rainbow_ma(market_data)
plot_rainbow(ma_list)
generate_signals(market_data, ma_list)
draw()

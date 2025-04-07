import random

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from datetime import datetime

from .models import PlotType, ActionType
from .plotter import PLOT_DATA
from .fetch import MARKET_DATA
from .strategy import STRATEGY_DATA

COLOR_PALETTE = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]

ASSIGNED_COLORS = {}


def get_color(label):
    """Assign a consistent random color for each label."""
    if label not in ASSIGNED_COLORS:
        ASSIGNED_COLORS[label] = random.choice(COLOR_PALETTE)
    return ASSIGNED_COLORS[label]


def draw():
    """Draw all charts from the PLOT_DATA and MARKET_DATA."""
    fig, ax = plt.subplots(figsize=(12, 6))

    def convert_timestamp(timestamp):
        if isinstance(timestamp, str):
            return mdates.date2num(datetime.fromisoformat(timestamp))
        return mdates.date2num(timestamp)

    plotted_histograms = set()
    for plot in PLOT_DATA.get(PlotType.HISTOGRAM, []):
        timestamps = [convert_timestamp(item["timestamp"]) for item in plot["data"]]
        values = [item["value"] for item in plot["data"]]

        if len(timestamps) > 1:
            bar_width = (max(timestamps) - min(timestamps)) / len(timestamps) * 0.8
        else:
            bar_width = 0.5

        label = (
            plot["label"] if plot["label"] not in plotted_histograms else "_nolegend_"
        )
        plotted_histograms.add(plot["label"])

        ax.bar(
            timestamps,
            values,
            label=label,
            color=get_color(plot["label"]),
            width=bar_width,
            alpha=0.6,
        )

    for plot in PLOT_DATA.get(PlotType.LINE, []):
        timestamps = [convert_timestamp(item["timestamp"]) for item in plot["data"]]
        values = [item["value"] for item in plot["data"]]
        ax.plot(
            timestamps,
            values,
            label=plot["label"],
            color=get_color(plot["label"]),
            lw=2,
        )

    for plot in PLOT_DATA.get(PlotType.AREA, []):
        timestamps = [convert_timestamp(item["timestamp"]) for item in plot["data"]]
        values = [item["value"] for item in plot["data"]]
        ax.fill_between(
            timestamps,
            values,
            label=plot["label"],
            color=get_color(plot["label"]),
            alpha=0.3,
        )

    candle_lut = {}
    for item in MARKET_DATA.quotes:
        timestamp = item.timestamp
        ts_str = timestamp if isinstance(timestamp, str) else timestamp.isoformat()
        ts_num = convert_timestamp(timestamp)
        price = item.close

        color = "green" if item.close > item.open else "red"
        ax.vlines(ts_num, item.low, item.high, color=color, lw=1)
        ax.vlines(ts_num, item.open, item.close, color=color, lw=4)

        candle_lut[ts_str] = (ts_num, price)

    plotted_labels = set()

    def plot_arrow(ts, y, marker, color, label):
        display_label = label if label not in plotted_labels else "_nolegend_"
        plotted_labels.add(label)
        ax.plot(ts, y, marker=marker, color=color, markersize=8, label=display_label)

    for strategy in STRATEGY_DATA.get("strategy", []):
        for trade in strategy.get("data", []):
            if "timestamp" not in trade:
                continue

            ts_key = (
                trade["timestamp"]
                if isinstance(trade["timestamp"], str)
                else trade["timestamp"].isoformat()
            )

            if ts_key not in candle_lut:
                continue

            ts_num, price = candle_lut[ts_key]
            offset = price * 0.1
            direction = trade.get("action") or trade.get("value")

            if direction == ActionType.LONG.value:
                plot_arrow(ts_num, price - offset, "^", "blue", "LONG")
            elif direction == ActionType.SHORT.value:
                plot_arrow(ts_num, price + offset, "v", "purple", "SHORT")

    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.set_title("Market Data Visualizations")
    ax.legend()

    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=30, ha="right")

    plt.tight_layout()
    plt.show()

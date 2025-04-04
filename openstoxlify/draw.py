import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from datetime import datetime
from .models import PlotType
from .plotter import PLOT_DATA
from .fetch import CANDLESTICK_DATA


def draw():
    """Draw all charts from the PLOT_DATA and CANDLESTICK_DATA."""
    fig, ax = plt.subplots(figsize=(12, 6))

    def convert_timestamp(timestamp):
        """Convert timestamp to matplotlib date format."""
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
            timestamps, values, label=label, color="blue", width=bar_width, alpha=0.6
        )

    for plot in PLOT_DATA.get(PlotType.LINE, []):
        timestamps = [convert_timestamp(item["timestamp"]) for item in plot["data"]]
        values = [item["value"] for item in plot["data"]]
        ax.plot(timestamps, values, label=plot["label"], color="green", lw=2)

    for plot in PLOT_DATA.get(PlotType.AREA, []):
        timestamps = [convert_timestamp(item["timestamp"]) for item in plot["data"]]
        values = [item["value"] for item in plot["data"]]
        ax.fill_between(
            timestamps, values, label=plot["label"], color="orange", alpha=0.3
        )

    for item in CANDLESTICK_DATA:
        timestamp_numeric = convert_timestamp(item["timestamp"])
        color = "green" if item["close"] > item["open"] else "red"
        ax.vlines(timestamp_numeric, item["low"], item["high"], color=color, lw=1)
        ax.vlines(timestamp_numeric, item["open"], item["close"], color=color, lw=4)

    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.set_title("Market Data Visualizations")
    ax.legend()

    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=30, ha="right")  # Improve readability

    plt.tight_layout()
    plt.show()

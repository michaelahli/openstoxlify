import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

from datetime import datetime
from .models import PlotType
from .plotter import PLOT_DATA
from .fetch import CANDLESTICK_DATA


def draw():
    """Draw all charts from the PLOT_DATA and CANDLESTICK_DATA."""
    fig, ax = plt.subplots(figsize=(14, 7))

    def convert_timestamp(timestamp):
        """Convert timestamp to matplotlib date format."""
        if isinstance(timestamp, str):
            return mdates.date2num(datetime.fromisoformat(timestamp))
        return mdates.date2num(timestamp)

    for plot in PLOT_DATA.get(PlotType.HISTOGRAM, []):
        for item in plot["data"]:
            ax.bar(
                convert_timestamp(item["timestamp"]),
                item["value"],
                label=plot["label"],
                color="blue",
                width=0.5,
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

    plt.xticks(rotation=30, ha="right")
    ax.margins(x=0.02)
    plt.tight_layout()
    plt.show()

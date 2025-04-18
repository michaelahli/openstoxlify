import unittest

import matplotlib.dates as mdates
from unittest.mock import patch, ANY
from datetime import datetime

from openstoxlify.models import PlotType, ActionType, Quote
from openstoxlify.draw import draw
from openstoxlify.plotter import PLOT_DATA
from openstoxlify.fetch import MARKET_DATA
from openstoxlify.strategy import STRATEGY_DATA


class TestDrawFunction(unittest.TestCase):
    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.axes.Axes.vlines")
    @patch("matplotlib.axes.Axes.plot")
    @patch("matplotlib.axes.Axes.bar")
    @patch("matplotlib.axes.Axes.fill_between")
    def test_draw(self, mock_fill_between, mock_bar, mock_plot, mock_vlines, mock_show):
        """Test the draw function to ensure plotting methods are called with expected data."""

        timestamp = datetime(2025, 3, 26)
        expected_ts_num = mdates.date2num(timestamp)

        PLOT_DATA.clear()
        STRATEGY_DATA.clear()

        PLOT_DATA[PlotType.HISTOGRAM] = [
            {"label": "histogram", "data": [{"timestamp": timestamp, "value": 100}]}
        ]
        PLOT_DATA[PlotType.LINE] = [
            {"label": "line", "data": [{"timestamp": timestamp, "value": 200}]}
        ]
        PLOT_DATA[PlotType.AREA] = [
            {"label": "area", "data": [{"timestamp": timestamp, "value": 300}]}
        ]

        MARKET_DATA.quotes.append(
            Quote(timestamp=timestamp, open=100, close=200, low=50, high=250, volume=10)
        )

        STRATEGY_DATA["strategy"] = [
            {"data": [{"timestamp": timestamp, "action": ActionType.LONG.value}]}
        ]

        draw()

        mock_bar.assert_called_with(
            [expected_ts_num],
            [100],
            label="histogram",
            color=ANY,
            width=0.5,
            alpha=0.6,
        )

        mock_plot.assert_any_call(
            [expected_ts_num], [200], label="line", color=ANY, lw=2
        )

        mock_fill_between.assert_called_with(
            [expected_ts_num], [300], label="area", color=ANY, alpha=0.3
        )

        offset_price = 200 - (200 * 0.1)
        mock_plot.assert_any_call(
            expected_ts_num,
            offset_price,
            marker="^",
            color="blue",
            markersize=8,
            label="LONG",
        )


if __name__ == "__main__":
    unittest.main()

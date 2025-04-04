import unittest
import matplotlib.dates as mdates

from unittest.mock import patch, MagicMock
from datetime import datetime, time
from openstoxlify.models import PlotType
from openstoxlify.draw import draw
from openstoxlify.fetch import fetch
from openstoxlify.output import output
from openstoxlify.plotter import PLOT_DATA


class TestDrawFunction(unittest.TestCase):
    @patch("matplotlib.pyplot.show")
    @patch("matplotlib.axes.Axes.plot")
    @patch("matplotlib.axes.Axes.bar")
    @patch("matplotlib.pyplot.fill_between")
    @patch("matplotlib.pyplot.vlines")
    def test_draw(self, mock_vlines, mock_fill_between, mock_bar, mock_plot, mock_show):
        """Test the draw function to ensure that plotting methods are called correctly."""

        timestamp = datetime(2025, 3, 26, 0, 0, 0)
        PLOT_DATA[PlotType.HISTOGRAM] = [
            {"label": "histogram", "data": [{"timestamp": timestamp, "value": 100}]}
        ]
        PLOT_DATA[PlotType.LINE] = [
            {"label": "line", "data": [{"timestamp": timestamp, "value": 200}]}
        ]
        PLOT_DATA[PlotType.AREA] = [
            {"label": "area", "data": [{"timestamp": timestamp, "value": 300}]}
        ]
        PLOT_DATA[PlotType.CANDLESTICK] = [
            {
                "label": "candlestick",
                "data": [
                    {
                        "timestamp": timestamp,
                        "open": 10,
                        "high": 15,
                        "low": 5,
                        "close": 12,
                    }
                ],
            }
        ]

        draw()

        expected_timestamp = mdates.date2num(datetime(2025, 3, 26, 0, 0, 0))

        mock_plot.assert_called_with(
            [expected_timestamp], [200], label="line", color="green", lw=2
        )

        mock_bar.assert_called_with(
            [expected_timestamp],
            [100],
            label="histogram",
            color="blue",
            width=0.5,
            alpha=0.6,
        )


if __name__ == "__main__":
    unittest.main()

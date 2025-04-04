import unittest
import json

from datetime import datetime
from unittest.mock import patch
from openstoxlify import (
    PlotType,
    ActionType,
    act,
    plot,
    STRATEGY_DATA,
    PLOT_DATA,
    output,
)


class TestStrategy(unittest.TestCase):
    def setUp(self):
        PLOT_DATA.clear()
        STRATEGY_DATA.clear()

    def test_plot(self):
        timestamp = datetime(2025, 3, 26, 0, 0, 0)
        value = 90000.0

        plot(PlotType.HISTOGRAM, "test_plot", timestamp, value)

        self.assertEqual(len(PLOT_DATA[PlotType.HISTOGRAM][0]["data"]), 1)
        self.assertEqual(
            PLOT_DATA[PlotType.HISTOGRAM][0]["data"][0]["timestamp"],
            timestamp.isoformat(),
        )
        self.assertEqual(PLOT_DATA[PlotType.HISTOGRAM][0]["data"][0]["value"], value)

    def test_act(self):
        timestamp = datetime(2025, 3, 26, 0, 0, 0)

        act(ActionType.LONG, timestamp)

        self.assertEqual(len(STRATEGY_DATA["strategy"][0]["data"]), 1)
        self.assertEqual(
            STRATEGY_DATA["strategy"][0]["data"][0]["action"], ActionType.LONG.value
        )
        self.assertEqual(
            STRATEGY_DATA["strategy"][0]["data"][0]["timestamp"], timestamp.isoformat()
        )

        act(ActionType.HOLD, timestamp)

        self.assertEqual(len(STRATEGY_DATA["strategy"][0]["data"]), 2)
        self.assertEqual(
            STRATEGY_DATA["strategy"][0]["data"][1]["action"], ActionType.HOLD.value
        )
        self.assertEqual(
            STRATEGY_DATA["strategy"][0]["data"][1]["timestamp"], timestamp.isoformat()
        )

    @patch("builtins.print")
    def test_output(self, mock_print):
        plot(PlotType.HISTOGRAM, "test_output", datetime(2025, 3, 26), 90000)
        act(ActionType.LONG, datetime(2025, 3, 26))

        output()

        actual_output = mock_print.call_args[0][0].strip()

        expected_output = json.dumps(
            {
                "histogram": [
                    {
                        "label": "test_output",
                        "data": [{"timestamp": "2025-03-26T00:00:00", "value": 90000}],
                    }
                ],
                "line": [],
                "area": [],
                "strategy": [
                    {
                        "label": "strategy",
                        "data": [
                            {"timestamp": "2025-03-26T00:00:00", "action": "Long"}
                        ],
                    }
                ],
            }
        )

        self.assertEqual(expected_output, actual_output)


if __name__ == "__main__":
    unittest.main()

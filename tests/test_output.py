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
        # Reset PLOT_DATA and STRATEGY_DATA before each test
        PLOT_DATA.clear()
        STRATEGY_DATA.clear()

    def test_plot(self):
        # Simulate calling plot function
        timestamp = datetime(2025, 3, 26, 0, 0, 0)
        value = 90000.0

        # We assume plot function adds the value to the correct plot type
        plot(PlotType.HISTOGRAM, timestamp, value)

        # Check if PLOT_DATA has been updated correctly
        self.assertEqual(len(PLOT_DATA[PlotType.HISTOGRAM][0]["data"]), 1)
        self.assertEqual(
            PLOT_DATA[PlotType.HISTOGRAM][0]["data"][0]["timestamp"],
            timestamp.isoformat(),
        )
        self.assertEqual(PLOT_DATA[PlotType.HISTOGRAM][0]["data"][0]["value"], value)

    def test_act(self):
        timestamp = datetime(2025, 3, 26, 0, 0, 0)

        # Test with Action.LONG
        act(ActionType.LONG, timestamp)

        # Check if STRATEGY_DATA has been updated
        self.assertEqual(len(STRATEGY_DATA["strategy"][0]["data"]), 1)
        self.assertEqual(
            STRATEGY_DATA["strategy"][0]["data"][0]["action"], ActionType.LONG.value
        )
        self.assertEqual(
            STRATEGY_DATA["strategy"][0]["data"][0]["timestamp"], timestamp.isoformat()
        )

        # Test with Action.HOLD
        act(ActionType.HOLD, timestamp)

        # Check if STRATEGY_DATA has been updated again
        self.assertEqual(len(STRATEGY_DATA["strategy"][0]["data"]), 2)
        self.assertEqual(
            STRATEGY_DATA["strategy"][0]["data"][1]["action"], ActionType.HOLD.value
        )
        self.assertEqual(
            STRATEGY_DATA["strategy"][0]["data"][1]["timestamp"], timestamp.isoformat()
        )

    @patch("builtins.print")
    def test_output(self, mock_print):
        # Simulate data in PLOT_DATA and STRATEGY_DATA
        plot(PlotType.HISTOGRAM, datetime(2025, 3, 26), 90000)
        act(ActionType.LONG, datetime(2025, 3, 26))

        # Call output function (which will call mock_print)
        output()

        # Get the actual output from the mock
        actual_output = mock_print.call_args[0][0].strip()

        # Convert actual_output and expected_output to compact JSON format
        expected_output = json.dumps(
            {
                "histogram": [
                    {
                        "label": "histogram",
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

        # Normalize both actual and expected to compact JSON format for comparison
        self.assertEqual(expected_output, actual_output)


if __name__ == "__main__":
    unittest.main()

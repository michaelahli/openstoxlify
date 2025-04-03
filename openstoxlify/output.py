import json
from .plotter import PLOT_DATA
from .strategy import STRATEGY_DATA
from .models import PlotType


def output():
    """Generate the final output as JSON."""
    result = {}

    # Process plot data (histogram, line, area)
    result["histogram"] = [
        {"label": plot["label"], "data": [item for item in plot["data"]]}
        for plot in PLOT_DATA.get(PlotType.HISTOGRAM, [])
    ]

    result["line"] = [
        {"label": plot["label"], "data": [item for item in plot["data"]]}
        for plot in PLOT_DATA.get(PlotType.LINE, [])
    ]

    result["area"] = [
        {"label": plot["label"], "data": [item for item in plot["data"]]}
        for plot in PLOT_DATA.get(PlotType.AREA, [])
    ]

    # Process strategy data (e.g., actions)
    result["strategy"] = [
        {
            "label": entry["label"],
            "data": [action for action in entry["data"]],
        }
        for entry in STRATEGY_DATA.get("strategy", [])
    ]

    # Print the result as JSON
    print(json.dumps(result))

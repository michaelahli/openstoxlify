import json
from .plotter import PLOT_DATA
from .strategy import STRATEGY_DATA
from .models import PlotType
from .fetch import MARKET_DATA


def output():
    """Generate the final output as JSON."""
    result = {}

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

    result["strategy"] = [
        {
            "label": entry["label"],
            "data": [action for action in entry["data"]],
        }
        for entry in STRATEGY_DATA.get("strategy", [])
    ]

    result["quotes"] = {
        "ticker": MARKET_DATA.ticker,
        "period": MARKET_DATA.period.value,
        "provider": MARKET_DATA.provider.value,
        "data": [
            {
                "timestamp": quote.timestamp.isoformat(),
                "open": quote.open,
                "high": quote.high,
                "low": quote.low,
                "close": quote.close,
            }
            for quote in MARKET_DATA.quotes
        ],
    }

    print(json.dumps(result))

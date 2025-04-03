from datetime import datetime
from .models import ActionType, ActionSeries

# Store strategy actions
STRATEGY_DATA = {}


def act(action: ActionType, timestamp: datetime):
    """Record an action taken at a specific timestamp."""
    if "strategy" not in STRATEGY_DATA:
        STRATEGY_DATA["strategy"] = [{"label": "strategy", "data": []}]

    STRATEGY_DATA["strategy"][0]["data"].append(
        ActionSeries(timestamp, action).to_dict()
    )

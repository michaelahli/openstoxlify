from .models import FloatSeries, PlotType
from datetime import datetime

PLOT_DATA = {}


def plot(graph_type: PlotType, timestamp: datetime, value: float):
    """Store data for plotting."""
    if graph_type not in PlotType:
        raise ValueError(f"Invalid graph type: {graph_type}")

    # Initialize the list if the graph type does not exist
    if graph_type not in PLOT_DATA:
        PLOT_DATA[graph_type] = [{"label": graph_type.value, "data": []}]

    # Convert FloatSeries to a dictionary before appending
    PLOT_DATA[graph_type][0]["data"].append(FloatSeries(timestamp, value).to_dict())

from .models import FloatSeries, PlotType
from datetime import datetime

PLOT_DATA = {PlotType.HISTOGRAM: [], PlotType.LINE: [], PlotType.AREA: []}


def plot(graph_type: PlotType, timestamp: datetime, value: float):
    """Store data for plotting."""
    if graph_type not in PlotType:
        raise ValueError(f"Invalid graph type: {graph_type}")

    # Initialize the list if the graph type does not exist
    if graph_type not in PLOT_DATA:
        PLOT_DATA[graph_type] = [{"label": graph_type.value, "data": []}]

    # Append the data to the respective plot type
    PLOT_DATA[graph_type][0]["data"].append(FloatSeries(timestamp, value))

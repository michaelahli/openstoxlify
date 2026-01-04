from typing import Dict, List
from ..models.model import Period, RangeInterval


def find_range_interval(period: Period) -> RangeInterval:
    dictionary: Dict[Period, RangeInterval] = {
        Period.MINUTELY: RangeInterval("1m", "1wk"),
        Period.QUINTLY: RangeInterval("5m", "1wk"),
        Period.HALFHOURLY: RangeInterval("30m", "1wk"),
        Period.HOURLY: RangeInterval("60m", "1wk"),
        Period.DAILY: RangeInterval("1d", "1y"),
        Period.WEEKLY: RangeInterval("1wk", "10y"),
        Period.MONTHLY: RangeInterval("1mo", "max"),
    }

    range_interval = dictionary.get(period)
    if range_interval is None:
        raise Exception(f"invalid period mapping {period}")

    return range_interval


def color_palette() -> List[str]:
    return [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
    ]

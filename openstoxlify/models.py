from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class PlotType(Enum):
    HISTOGRAM = "histogram"
    LINE = "line"
    AREA = "area"
    CANDLESTICK = "candlestick"


@dataclass
class Quote:
    timestamp: datetime
    high: float
    low: float
    open: float
    close: float


@dataclass
class MarketData:
    ticker: str
    quotes: list[Quote]


@dataclass
class FloatSeries:
    timestamp: datetime
    value: float

    def to_dict(self):
        return {"timestamp": self.timestamp.isoformat(), "value": self.value}


class ActionType(Enum):
    LONG = "Long"
    HOLD = "Hold"
    SHORT = "Short"


@dataclass
class ActionSeries:
    timestamp: datetime
    action: ActionType

    def to_dict(self):
        return {"timestamp": self.timestamp.isoformat(), "action": self.action.value}


@dataclass
class LabeledSeries:
    label: str
    data: list

    def to_dict(self):
        return {"label": self.label, "data": [item.to_dict() for item in self.data]}


@dataclass
class Output:
    histogram: list[LabeledSeries]
    line: list[LabeledSeries]
    area: list[LabeledSeries]
    strategy: list[LabeledSeries]

    def to_dict(self):
        return {
            "histogram": [series.to_dict() for series in self.histogram]
            if self.histogram
            else None,
            "line": [series.to_dict() for series in self.line],
            "area": [series.to_dict() for series in self.area] if self.area else None,
            "strategy": [series.to_dict() for series in self.strategy]
            if self.strategy
            else None,
        }

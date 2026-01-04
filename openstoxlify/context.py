from typing import List, Dict

from .models.contract import Provider
from .models.enum import ActionType, PlotType
from .models.series import ActionSeries, FloatSeries
from .models.model import Period, PlotData, Quote


class Context:
    def __init__(self, provider: Provider, symbol: str, period: Period):
        self._symbol = symbol
        self._period = period
        self._provider = provider

        self._quotes: List[Quote] = []
        self._quotes_mapped: Dict[str, List[Quote]] = {}
        self._plots: Dict[str, List[PlotData]] = {}
        self._signals: List[ActionSeries] = []

        self._token: str = ""
        self._authenticated: bool = False

    def quotes(self) -> List[Quote]:
        quotes = self._quotes_mapped.get(self._symbol)
        if quotes is not None:
            return quotes

        self._quotes = self._provider.quotes(self._symbol, self._period)
        self._quotes_mapped[self._symbol] = self._quotes
        return self._quotes

    def plot(
        self, label: str, plot_type: PlotType, data: FloatSeries, screen_index: int = 0
    ):
        if plot_type not in PlotType:
            raise ValueError(f"Invalid plot type: {plot_type}")

        key = plot_type.value
        if key not in self._plots:
            self._plots[key] = []

        for plot_entry in self._plots[key]:
            if plot_entry.label == label:
                plot_entry.data.append(data)
                return

        self._plots[key].append(
            PlotData(label=label, data=[data], screen_index=screen_index)
        )

    def signal(self, data: ActionSeries):
        data.amount = 0.0 if data.action == ActionType.HOLD else data.amount

        self._signals.append(data)

    def authecticate(self, token: str):
        try:
            self._provider.authenticate(token)
            self._token = token
            self._authenticated = True
        except Exception:
            self._authenticated = False

    def execute(self):
        if not self._authenticated:
            return

        self._quotes.sort(key=lambda q: q.timestamp)
        latest = self._quotes[-1].timestamp
        hashmap = {s.timestamp: s for s in self._signals}

        signal = hashmap.get(latest)
        if signal is None:
            return

        match signal.action:
            case ActionType.HOLD:
                return

        self._provider.execute(self._symbol, signal, signal.amount)

    def plots(self) -> Dict[str, List[PlotData]]:
        return self._plots

    def signals(self) -> List[ActionSeries]:
        return self._signals

    def symbol(self) -> str:
        return self._symbol

    def period(self) -> Period:
        return self._period

    def provider(self) -> Provider:
        return self._provider

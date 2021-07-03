from __future__ import annotations
from abc import ABC, abstractmethod


class ILatencyListener(ABC):
    @abstractmethod
    def on_latency_available(self, latency: float) -> None:
        """"""

    @abstractmethod
    def on_latency_timeout(self) -> None:
        """"""


class ILatencyServerService(ABC):
    @abstractmethod
    def add_latency_listener(self, latency_listener: ILatencyListener) -> ILatencyServerService:
        """"""

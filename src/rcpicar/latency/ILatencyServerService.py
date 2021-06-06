from __future__ import annotations
from abc import ABC, abstractmethod
from .ILatencyListener import ILatencyListener


class ILatencyServerService(ABC):
    @abstractmethod
    def add_latency_listener(self, latency_listener: ILatencyListener) -> ILatencyServerService:
        """"""

from abc import ABC, abstractmethod


class ILatencyListener(ABC):
    @abstractmethod
    def on_latency_available(self, latency: float) -> None:
        """"""

    @abstractmethod
    def on_latency_timeout(self) -> None:
        """"""

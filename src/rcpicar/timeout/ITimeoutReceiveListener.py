from abc import ABC, abstractmethod


class ITimeoutReceiveListener(ABC):
    @abstractmethod
    def on_timeout_receive(self) -> None:
        """"""

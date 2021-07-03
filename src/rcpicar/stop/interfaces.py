from abc import ABC, abstractmethod


class IStopServerService(ABC):
    @abstractmethod
    def wait(self) -> None:
        """"""

from __future__ import annotations
from abc import ABC, abstractmethod
from .util.ConnectionDetails import ConnectionDetails


class IReceiveListener(ABC):
    @abstractmethod
    def on_receive(self, message: bytes, details: ConnectionDetails) -> None:
        """"""


class IReceiveService(ABC):
    @abstractmethod
    def add_receive_listener(self, listener: IReceiveListener) -> IReceiveService:
        """"""

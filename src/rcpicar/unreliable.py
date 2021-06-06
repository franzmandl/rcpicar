from __future__ import annotations
from abc import ABC, abstractmethod
from .receive import IReceiveService
from .send import ISendService
from .util.ConnectionDetails import ConnectionDetails


class IUnreliableOsErrorListener(ABC):
    @abstractmethod
    def on_unreliable_os_error(self, os_error: OSError) -> None:
        """"""


class IUnreliableReceiveListener(ABC):
    @abstractmethod
    def on_unreliable_receive(self, message: bytes, details: ConnectionDetails) -> None:
        """"""


class IUnreliableService(ABC):
    @abstractmethod
    def add_unreliable_os_error_listener(self, listener: IUnreliableOsErrorListener) -> IUnreliableService:
        """"""

    @abstractmethod
    def add_unreliable_receive_listener(self, listener: IUnreliableReceiveListener) -> IUnreliableService:
        """"""


class IUnreliableReceiveSendService(IReceiveService, ISendService, IUnreliableService, ABC):
    """"""

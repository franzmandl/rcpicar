from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Tuple
from .receive import IReceiveService
from .send import ISendService
from .util.ConnectionDetails import ConnectionDetails


class IReliableConnectListener(ABC):
    @abstractmethod
    def on_reliable_connect(self, details: ConnectionDetails) -> None:
        """"""


class IReliableDisconnectListener(ABC):
    @abstractmethod
    def on_reliable_disconnect(self, details: ConnectionDetails) -> None:
        """"""


class IReliableOsErrorListener(ABC):
    @abstractmethod
    def on_reliable_os_error(self, os_error: OSError) -> None:
        """"""


class IReliableReceiveListener(ABC):
    @abstractmethod
    def on_reliable_receive(self, message: bytes, details: ConnectionDetails) -> None:
        """"""


class IReliableService(ABC):
    @abstractmethod
    def add_reliable_connect_listener(self, listener: IReliableConnectListener) -> IReliableService:
        """"""

    @abstractmethod
    def add_reliable_disconnect_listener(self, listener: IReliableDisconnectListener) -> IReliableService:
        """"""

    @abstractmethod
    def add_reliable_os_error_listener(self, listener: IReliableOsErrorListener) -> IReliableService:
        """"""

    @abstractmethod
    def add_reliable_receive_listener(self, listener: IReliableReceiveListener) -> IReliableService:
        """"""

    @abstractmethod
    def get_own_address(self) -> Tuple[str, int]:
        """"""


class IReliableReceiveSendService(IReceiveService, IReliableService, ISendService, ABC):
    """"""

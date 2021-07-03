from __future__ import annotations
from abc import ABC, abstractmethod
from ..receive import IReceiveService
from ..send import ISendService
from ..util.ConnectionDetails import ConnectionDetails


class IRoutedReceiveListener(ABC):
    @abstractmethod
    def on_routed_receive(self, message_type: int, message: bytes, details: ConnectionDetails) -> None:
        """"""


class IRoutedReceiveService(ABC):
    @abstractmethod
    def add_receive_listener(self, message_type: int, listener: IRoutedReceiveListener) -> IRoutedReceiveService:
        """"""

    @abstractmethod
    def create_receive_service(self, message_type: int) -> IReceiveService:
        """"""


class IRoutedSendService(ABC):
    @abstractmethod
    def create_send_service(self, message_type: int) -> ISendService:
        """"""

    @abstractmethod
    def send(self, message_type: int, message: bytes) -> None:
        """"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable, Optional
from ..receive import IReceiveService


class ITimeoutReceiveListener(ABC):
    @abstractmethod
    def on_timeout_receive(self) -> None:
        """"""


class ITimeoutReceiveService(IReceiveService, ABC):
    @abstractmethod
    def add_timeout_listener(self, timeout_listener: ITimeoutReceiveListener) -> ITimeoutReceiveService:
        """"""

    @abstractmethod
    def set_timeout(self, timeout_seconds: float) -> None:
        """"""


class ITimeoutSendService(ABC):
    @abstractmethod
    def get_send_count(self) -> int:
        """"""

    @abstractmethod
    def set_and_send_immediately(self, message_callback: Callable[[], Optional[bytes]]) -> Optional[bytes]:
        """"""

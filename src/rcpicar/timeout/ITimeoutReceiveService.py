from __future__ import annotations
from abc import ABC, abstractmethod
from .ITimeoutReceiveListener import ITimeoutReceiveListener


class ITimeoutReceiveService(ABC):
    @abstractmethod
    def add_timeout_listener(self, timeout_listener: ITimeoutReceiveListener) -> ITimeoutReceiveService:
        """"""

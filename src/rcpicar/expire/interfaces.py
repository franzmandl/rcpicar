from __future__ import annotations
from abc import ABC, abstractmethod
from ..receive import IReceiveService
from ..util.ConnectionDetails import ConnectionDetails


class IExpireReceiveListener(ABC):
    @abstractmethod
    def on_expire_receive(self, message: bytes, details: ConnectionDetails) -> None:
        """"""


class IExpireReceiveService(IReceiveService, ABC):
    @abstractmethod
    def add_expire_listener(self, listener: IExpireReceiveListener) -> IExpireReceiveService:
        """"""

    @abstractmethod
    def reset(self) -> None:
        """"""

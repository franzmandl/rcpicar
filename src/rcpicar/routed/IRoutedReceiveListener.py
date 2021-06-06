from __future__ import annotations
from abc import ABC, abstractmethod
from ..util.ConnectionDetails import ConnectionDetails


class IRoutedReceiveListener(ABC):
    @abstractmethod
    def on_routed_receive(self, message_type: int, message: bytes, details: ConnectionDetails) -> None:
        """"""

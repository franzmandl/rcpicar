from __future__ import annotations
from abc import ABC, abstractmethod


class ISendService(ABC):
    @abstractmethod
    def send(self, message: bytes) -> None:
        """"""

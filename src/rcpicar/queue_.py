from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

T = TypeVar('T')


class IQueue(Generic[T], ABC):
    @abstractmethod
    def empty(self) -> bool:
        """"""

    @abstractmethod
    def get(self, block: bool = True, timeout: Optional[float] = None) -> T:
        """"""

    @abstractmethod
    def join(self) -> None:
        """"""

    @abstractmethod
    def put(self, item: T) -> None:
        """"""

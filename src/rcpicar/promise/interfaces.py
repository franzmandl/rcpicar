from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

T = TypeVar('T')


class IPromise(Generic[T], ABC):
    @abstractmethod
    def get_blocking(self) -> Optional[T]:
        """"""

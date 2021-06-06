from typing import Generic, List, Optional, TypeVar
from .Atomic import Atomic

T = TypeVar('T')


class FirstInLastOut(Generic[T]):
    """
    Thread-safe first-in-last-out
    """
    def __init__(self) -> None:
        self._filo: Atomic[List[T]] = Atomic([])

    def append(self, item: T) -> None:
        with self._filo as (filo, _):
            filo.append(item)

    def pop(self) -> Optional[T]:
        with self._filo as (filo, _):
            if len(filo) == 0:
                return None
            return filo.pop()

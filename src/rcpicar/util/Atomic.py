from threading import Lock
from types import TracebackType
from typing import Callable, Generic, Optional, Tuple, Type, TypeVar

T = TypeVar('T')


class Atomic(Generic[T]):
    def __init__(self, value: T) -> None:
        self._lock = Lock()
        self._value = value

    def __enter__(self) -> Tuple[T, Callable[[T], T]]:
        self._lock.__enter__()
        return self._value, self._set_value

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType]
    ) -> None:
        self._lock.__exit__(exc_type, exc_val, exc_tb)

    def get(self) -> T:
        return self._value

    def _set_value(self, value: T) -> T:
        self._value = value
        return value

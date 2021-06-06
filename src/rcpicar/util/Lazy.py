from __future__ import annotations
from typing import Callable, Generic, Optional, TypeVar

T = TypeVar('T')


class Lazy(Generic[T]):
    def __init__(self, compute_default: Callable[[bool], T]) -> None:
        self._compute_default = compute_default
        self._is_computing = False
        self._value: Optional[T] = None

    def __call__(self, store: bool) -> T:
        if self._value is None:
            if self._is_computing:
                raise RuntimeError('Circular dependency detected. See stacktrace.')
            self._is_computing = True
            value = self._compute_default(store)
            self._is_computing = False
            if store:
                self._value = value
            return value
        else:
            return self._value

    def get_default(self) -> T:
        return self(False)

    def get(self) -> T:
        return self(True)

    def set(self, value: T) -> None:
        self._value = value

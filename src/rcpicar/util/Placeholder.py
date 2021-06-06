from types import TracebackType
from typing import Callable, Generic, Optional, Tuple, Type, TypeVar
from .Atomic import Atomic
from .FirstInLastOut import FirstInLastOut
from ..service import AbstractServiceManager
from ..promise.IPromise import IPromise
from ..promise.PromiseService import PromiseService

T = TypeVar('T')


class Placeholder(Generic[T]):
    def __init__(self, initial_value: Optional[T] = None) -> None:
        self._promises: FirstInLastOut[PromiseService[T]] = FirstInLastOut()
        self._value = Atomic(initial_value)

    def clear(self) -> None:
        with self._value as (_, set_optional):
            set_optional(None)

    def clear_and_set(self, next_optional: T) -> None:
        with self._value as (current_optional, set_optional):
            set_optional(None)
            _set(current_optional, next_optional, set_optional, self._promises)

    def get(self) -> T:
        with self._value as (optional, _):
            return _get(optional)

    def get_and_clear(self) -> T:
        with self._value as (optional, set_optional):
            return _get_and_clear(optional, set_optional)

    def get_eventually(self, service_manager: AbstractServiceManager) -> IPromise[T]:
        promise: PromiseService[T] = PromiseService(service_manager)
        with self._value as (optional, _):
            if optional is None:
                self._promises.append(promise)
            else:
                promise.resolve(optional)
        return promise

    def get_optional(self) -> Optional[T]:
        with self._value as (optional, _):
            return optional

    def get_optional_and_clear(self) -> Optional[T]:
        with self._value as (optional, set_optional):
            set_optional(None)
            return optional

    def is_present(self) -> bool:
        with self._value as (optional, _):
            return optional is not None

    def set(self, next_optional: T) -> T:
        with self._value as (current_optional, set_optional):
            _set(current_optional, next_optional, set_optional, self._promises)
        return next_optional

    def __enter__(self) -> Tuple[Optional[T], Callable[[Optional[T]], Optional[T]]]:
        return self._value.__enter__()

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType]
    ) -> None:
        self._value.__exit__(exc_type, exc_val, exc_tb)


def _get(optional: Optional[T]) -> T:
    if optional is None:
        raise RuntimeError('Placeholder is empty')
    return optional


def _get_and_clear(
        optional: Optional[T],
        set_optional: Callable[[Optional[T]], Optional[T]],
) -> T:
    try:
        return _get(optional)
    finally:
        set_optional(None)


def _set(
        current_optional: Optional[T],
        next_optional: T,
        set_optional: Callable[[Optional[T]], Optional[T]],
        promises: FirstInLastOut[PromiseService[T]],
) -> None:
    if current_optional is not None:
        raise RuntimeError('Placeholder is not empty')
    set_optional(next_optional)
    while True:
        promise = promises.pop()
        if promise is None:
            break
        promise.resolve(next_optional)

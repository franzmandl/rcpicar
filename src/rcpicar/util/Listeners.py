from logging import getLogger
from typing import Callable, Generic, List, TypeVar

T = TypeVar('T')


class Listeners(Generic[T]):
    def __init__(self) -> None:
        self.listeners: List[T] = []
        self.logger = getLogger(__name__)

    def add_listener(self, listener: T) -> None:
        self.listeners.append(listener)

    def for_each(self, callback: Callable[[T], None]) -> None:
        for listener in self.listeners:
            try:
                callback(listener)
            except BaseException as exception:
                self.logger.exception(f'Exception thrown in listener callback:', exc_info=exception)

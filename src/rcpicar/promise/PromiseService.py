from __future__ import annotations
from threading import Event
from typing import Generic, Optional, TypeVar
from .IPromise import IPromise
from ..service import AbstractStartedService, AbstractServiceManager

T = TypeVar('T')


class PromiseService(Generic[T], IPromise[T], AbstractStartedService):
    def __init__(self, service_manager: AbstractServiceManager) -> None:
        super().__init__(service_manager)
        self._event = Event()
        self._value: Optional[T] = None

    def get_blocking(self) -> Optional[T]:
        self._event.wait()
        return self._value

    def get_service_name(self) -> str:
        return __name__

    def join_service(self, timeout_seconds: Optional[float] = None) -> bool:
        return self._event.is_set()

    def reject(self) -> IPromise[T]:
        self._event.set()
        return self

    def resolve(self, value: T) -> IPromise[T]:
        self._value = value
        self._event.set()
        return self

    def stop_service(self) -> None:
        self.reject()

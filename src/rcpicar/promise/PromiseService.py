from __future__ import annotations
from threading import Event
from typing import Generic, Optional, TypeVar
from .interfaces import IPromise
from ..service import IStartedService, IServiceManager

T = TypeVar('T')


class PromiseService(Generic[T], IPromise[T], IStartedService):
    def __init__(self, service_manager: IServiceManager) -> None:
        self._event = Event()
        self._value: Optional[T] = None
        service_manager.add_started_service(self)

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

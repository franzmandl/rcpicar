from abc import ABC, abstractmethod
from threading import Event, Lock, Thread
from typing import ContextManager, Optional, TypeVar
from .queue_ import IQueue
from .service import IServiceManager

T = TypeVar('T')


class IClock(ABC):
    @abstractmethod
    def acquire_lock(self, lock: Lock, timeout_seconds: Optional[float] = None) -> bool:
        """"""

    @abstractmethod
    def get_from_queue(self, queue: IQueue[T], timeout_seconds: Optional[float] = None) -> T:
        """"""

    @abstractmethod
    def get_seconds(self) -> float:
        """"""

    @abstractmethod
    def join_thread(self, thread: Thread, timeout_seconds: Optional[float] = None) -> None:
        """"""

    @abstractmethod
    def use_services(self, service_manager: IServiceManager) -> ContextManager[None]:
        """"""

    @abstractmethod
    def wait_for_event(self, event: Event, timeout_seconds: Optional[float] = None) -> bool:
        """"""

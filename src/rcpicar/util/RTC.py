from datetime import datetime
from threading import Event, Lock, Thread
from types import TracebackType
from typing import ContextManager, Optional, Type, TypeVar
from ..clock import IClock
from ..queue_ import IQueue
from ..service import IServiceManager

T = TypeVar('T')


class _RTC(IClock):
    """
    Real-time clock
    """
    def acquire_lock(self, lock: Lock, timeout_seconds: Optional[float] = None) -> bool:
        if timeout_seconds is None:
            return lock.acquire()
        else:
            return lock.acquire(timeout=timeout_seconds)

    def get_from_queue(self, queue: IQueue[T], timeout_seconds: Optional[float] = None) -> T:
        return queue.get(timeout=timeout_seconds)

    def get_seconds(self) -> float:
        return datetime.utcnow().timestamp()

    def join_thread(self, thread: Thread, timeout_seconds: Optional[float] = None) -> None:
        thread.join(timeout_seconds)

    def use_services(self, service_manager: IServiceManager) -> ContextManager[None]:
        return Context(service_manager)

    def wait_for_event(self, event: Event, timeout_seconds: Optional[float] = None) -> bool:
        return event.wait(timeout_seconds)


rtc = _RTC()


class Context:
    def __init__(self, service_manager: IServiceManager) -> None:
        self.service_manager = service_manager

    def __enter__(self) -> None:
        self.service_manager.start_all()

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType]
    ) -> None:
        self.service_manager.stop_all()
        self.service_manager.join_all()

from datetime import datetime
from threading import Event, Lock, Thread
from typing import Optional, TypeVar
from ..clock import IClock
from ..queue_ import IQueue

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

    def notify(self) -> None:
        pass

    def wait_for_event(self, event: Event, timeout_seconds: Optional[float] = None) -> bool:
        return event.wait(timeout_seconds)


rtc = _RTC()

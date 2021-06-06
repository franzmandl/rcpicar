from queue import Empty
from threading import Condition, Event, Lock, Thread
from time import sleep
from typing import Any, Callable, Optional, Set, TypeVar
from rcpicar.clock import IClock
from rcpicar.queue_ import IQueue

T = TypeVar('T')


class MockClock(IClock):
    def __init__(self, tick_seconds: float = 0.1) -> None:
        self.cv = Condition()
        self.ticks = 0
        self.tick_seconds = tick_seconds
        self.waiting_queues: Set[IQueue[Any]] = set()

    def acquire_lock(self, lock: Lock, timeout_seconds: Optional[float] = None) -> bool:
        if timeout_seconds is None:
            return lock.acquire()
        else:
            with self.cv:
                end_seconds = self.get_seconds() + timeout_seconds
                while self.get_seconds() < end_seconds:
                    if lock.acquire(False):
                        return True
                    self.cv.wait()
            return lock.acquire(False)

    def get_from_queue(self, queue: IQueue[T], timeout_seconds: Optional[float] = None) -> T:
        try:
            self.waiting_queues.add(queue)
            if timeout_seconds is None:
                return queue.get()
            else:
                with self.cv:
                    end_seconds = self.get_seconds() + timeout_seconds
                    while self.get_seconds() < end_seconds:
                        try:
                            return queue.get(block=False)
                        except Empty:
                            pass
                        self.cv.wait()
                return queue.get(block=False)
        finally:
            self.waiting_queues.remove(queue)

    def get_seconds(self) -> float:
        return self.ticks * self.tick_seconds

    def join_thread(self, thread: Thread, timeout_seconds: Optional[float] = None) -> None:
        if timeout_seconds is None:
            thread.join()
        else:
            with self.cv:
                end_seconds = self.get_seconds() + timeout_seconds
                while self.get_seconds() < end_seconds:
                    if not thread.is_alive():
                        return
                    self.cv.wait()

    def notify(self) -> None:
        with self.cv:
            self.cv.notify_all()

    def notify_till(self, condition: Callable[[], bool]) -> None:
        while not condition():
            sleep(self.tick_seconds)
            self.notify()

    def sleep_till(self, condition: Callable[[], bool]) -> None:
        while not condition():
            sleep(self.tick_seconds)

    def tick(self, count: int = 1) -> None:
        with self.cv:
            self.ticks += count
            self.cv.notify_all()

    def wait_for_event(self, event: Event, timeout_seconds: Optional[float] = None) -> bool:
        if timeout_seconds is None:
            return event.wait()
        else:
            with self.cv:
                end_seconds = self.get_seconds() + timeout_seconds
                while self.get_seconds() < end_seconds:
                    if event.is_set():
                        return True
                    self.cv.wait()
            return False

from queue import Empty, Queue
from sys import version_info
from typing import Generic, Optional, TypeVar
from ..queue_ import IQueue

T = TypeVar('T')


class IdealQueue(Generic[T], IQueue[T]):
    def __init__(self) -> None:
        self._call_task_done = False
        if version_info >= (3, 8):
            queue: Queue[T] = Queue()
        else:
            queue = Queue()
        self._queue = queue

    def empty(self) -> bool:
        return self._queue.empty()

    def get(self, block: bool = True, timeout: Optional[float] = None) -> T:
        call_task_done = self._call_task_done
        self._call_task_done = True
        if call_task_done:
            self._queue.task_done()
        try:
            return self._queue.get(block=block, timeout=timeout)
        except Empty as exception:
            self._call_task_done = False
            raise exception

    def join(self) -> None:
        self._queue.join()

    def put(self, item: T) -> None:
        self._queue.put(item)

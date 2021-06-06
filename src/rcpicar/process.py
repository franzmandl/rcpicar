from abc import ABC, abstractmethod
from typing import Callable, IO, Optional, Sequence, Union


class IProcess(ABC):
    @abstractmethod
    def get_stdout(self) -> IO[bytes]:
        """"""

    @abstractmethod
    def terminate(self) -> None:
        """"""

    @abstractmethod
    def wait(self, timeout: Optional[float]) -> None:
        """"""


FILE = Union[int, IO[bytes]]
ProcessFactory = Callable[[Sequence[str], Optional[FILE], Optional[FILE]], IProcess]

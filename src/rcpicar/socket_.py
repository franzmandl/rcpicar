from __future__ import annotations
from abc import ABC, abstractmethod
from socket import SHUT_RDWR
from types import TracebackType
from typing import Callable, Optional, Tuple, Type, Union


class ISocket(ABC):
    @abstractmethod
    def __enter__(self) -> ISocket:
        """"""

    @abstractmethod
    def __exit__(
            self, exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType]
    ) -> None:
        """"""

    @abstractmethod
    def accept(self) -> Tuple[ISocket, Tuple[str, int]]:
        """"""

    @abstractmethod
    def bind(self, address: Tuple[str, int]) -> None:
        """"""

    @abstractmethod
    def close(self) -> None:
        """"""

    @abstractmethod
    def connect(self, address: Tuple[str, int]) -> None:
        """"""

    @abstractmethod
    def getsockname(self) -> Tuple[str, int]:
        """"""

    @abstractmethod
    def listen(self, backlog: int) -> None:
        """"""

    @abstractmethod
    def recv(self, bufsize: int) -> bytes:
        """"""

    @abstractmethod
    def recvfrom(self, bufsize: int) -> Tuple[bytes, Optional[Tuple[str, int]]]:
        """"""

    @abstractmethod
    def sendall(self, data: bytes) -> None:
        """"""

    @abstractmethod
    def sendto(self, data: bytes, address: Tuple[str, int]) -> int:
        """"""

    @abstractmethod
    def setsockopt(self, level: int, optname: int, value: Union[int, bytes]) -> None:
        """"""

    @abstractmethod
    def settimeout(self, value: float) -> None:
        """"""

    @abstractmethod
    def shutdown(self, how: int) -> None:
        """"""

    def shutdown_guaranteed(self, on_os_error: Callable[[OSError], None] = lambda os_error: None) -> None:
        try:
            # Notifies recvfrom() that the socket is shutdown, but shutdown on UDP sockets always throws an OSError,
            # but recvfrom() returns (b'', None) in such case.
            self.shutdown(SHUT_RDWR)
        except OSError as os_error:
            on_os_error(os_error)


class ISocketFactory(ABC):
    @abstractmethod
    def socket(self, family: int, type_: int, proto: int = -1) -> ISocket:
        """"""

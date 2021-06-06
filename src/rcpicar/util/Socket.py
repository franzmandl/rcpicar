from __future__ import annotations
from socket import socket
from types import TracebackType
from typing import Callable, Optional, Tuple, Type, Union
from ..socket_ import ISocket, ISocketFactory
from ..util.checking import check_type_tuple2


class Socket(ISocket):
    def __init__(self, socket_: socket) -> None:
        self.socket = socket_

    def __enter__(self) -> Socket:
        return Socket(self.socket.__enter__())

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType]
    ) -> None:
        self.socket.__exit__(exc_type, exc_val, exc_tb)

    def accept(self) -> Tuple[Socket, Tuple[str, int]]:
        socket_, address = self.socket.accept()
        return Socket(socket_), address

    def bind(self, address: Tuple[str, int]) -> None:
        self.socket.bind(address)

    def close(self) -> None:
        self.socket.close()

    def connect(self, address: Tuple[str, int]) -> None:
        self.socket.connect(address)

    def getsockname(self) -> Tuple[str, int]:
        return check_type_tuple2(self.socket.getsockname(), str, int)

    def listen(self, backlog: int) -> None:
        self.socket.listen(backlog)

    def recv(self, bufsize: int) -> bytes:
        return self.socket.recv(bufsize)

    def recvfrom(self, bufsize: int) -> Tuple[bytes, Tuple[str, int]]:
        return self.socket.recvfrom(bufsize)

    def sendall(self, data: bytes) -> None:
        self.socket.sendall(data)

    def sendto(self, data: bytes, address: Tuple[str, int]) -> int:
        return self.socket.sendto(data, address)

    def setsockopt(self, level: int, optname: int, value: Union[int, bytes]) -> None:
        self.socket.setsockopt(level, optname, value)

    def settimeout(self, value: float) -> None:
        self.socket.settimeout(value)

    def shutdown(self, how: int) -> None:
        self.socket.shutdown(how)


class SocketFactory(ISocketFactory):
    def __init__(self, socket_factory: Callable[[int, int, int], socket]) -> None:
        self.socket_factory = socket_factory

    def socket(self, family: int, type_: int, proto: int = -1) -> Socket:
        return Socket(self.socket_factory(family, type_, proto))

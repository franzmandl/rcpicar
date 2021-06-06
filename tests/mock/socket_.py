from __future__ import annotations
from types import TracebackType
from typing import Optional, Tuple, Type, Union
from rcpicar.socket_ import ISocket, ISocketFactory
from rcpicar.util.checking import check_message_length
from rcpicar.queue_ import IQueue
from tests.suite.spy import FunctionSpy


class MockSocket(ISocket):
    @staticmethod
    def create_dummy(own_address: Tuple[str, int]) -> MockSocket:
        mock = MockSocket()
        mock.enter___spy.constant(mock)
        mock.exit___spy.constant(None)
        mock.close_spy.constant(None)
        mock.getsockname_spy.constant(own_address)
        mock.setsockopt_spy.constant(None)
        mock.settimeout_spy.constant(None)
        return mock

    @staticmethod
    def create_tcp_server(
            accept_socket: ISocket,
            own_address: Tuple[str, int],
            peer_address: Tuple[str, int],
    ) -> MockSocket:
        mock = MockSocket.create_dummy(own_address)
        mock.accept_spy.constant((accept_socket, peer_address))
        mock.bind_spy.constant(None)
        mock.listen_spy.constant(None)
        mock.shutdown_spy.constant(None)
        return mock

    @staticmethod
    def create_tcp_tunnel(
            own_address: Tuple[str, int],
            receive_queue: IQueue[bytes],
            send_queue: IQueue[bytes]
    ) -> MockSocket:
        mock = MockSocket.create_dummy(own_address)

        def recv(args: Tuple[int]) -> bytes:
            bufsize, = args
            check_message_length(bufsize)
            return receive_queue.get()

        mock.recv_spy.callback(recv)

        def sendall(args: Tuple[bytes]) -> int:
            data, = args
            check_message_length(len(data))
            send_queue.put(data)
            return len(data)

        mock.sendall_spy.callback(sendall)
        mock.shutdown_spy.callback(lambda args: receive_queue.put(b''))
        return mock

    @staticmethod
    def create_tcp_client(
            own_address: Tuple[str, int],
            receive_queue: IQueue[bytes],
            send_queue: IQueue[bytes]
    ) -> MockSocket:
        mock = MockSocket.create_tcp_tunnel(own_address, receive_queue, send_queue)
        mock.connect_spy.constant(None)
        return mock

    @staticmethod
    def create_udp_tunnel(
            own_address: Tuple[str, int],
            receive_queue: IQueue[Tuple[bytes, Optional[Tuple[str, int]]]],
            send_queue: IQueue[Tuple[bytes, Optional[Tuple[str, int]]]]
    ) -> MockSocket:
        mock = MockSocket.create_dummy(own_address)

        def recvfrom(args: Tuple[int]) -> Tuple[bytes, Optional[Tuple[str, int]]]:
            bufsize, = args
            check_message_length(bufsize)
            return receive_queue.get()

        mock.recvfrom_spy.callback(recvfrom)

        def sendto(args: Tuple[bytes, Tuple[str, int]]) -> int:
            data, address = args
            check_message_length(len(data))
            send_queue.put((data, address))
            return len(data)

        mock.sendto_spy.callback(sendto)
        mock.shutdown_spy.callback(lambda args: receive_queue.put((b'', None)))
        return mock

    @staticmethod
    def create_udp_server(
            own_address: Tuple[str, int],
            receive_queue: IQueue[Tuple[bytes, Optional[Tuple[str, int]]]],
            send_queue: IQueue[Tuple[bytes, Optional[Tuple[str, int]]]]
    ) -> MockSocket:
        mock = MockSocket.create_udp_tunnel(own_address, receive_queue, send_queue)
        mock.bind_spy.constant(None)
        return mock

    def __init__(self) -> None:
        self.enter___spy: FunctionSpy[Tuple[()], ISocket] = FunctionSpy()
        self.exit___spy: FunctionSpy[
            Tuple[Optional[Type[BaseException]], Optional[BaseException], Optional[TracebackType]], None
        ] = FunctionSpy()
        self.accept_spy: FunctionSpy[Tuple[()], Tuple[ISocket, Tuple[str, int]]] = FunctionSpy()
        self.bind_spy: FunctionSpy[Tuple[Tuple[str, int]], None] = FunctionSpy()
        self.close_spy: FunctionSpy[Tuple[()], None] = FunctionSpy()
        self.connect_spy: FunctionSpy[Tuple[Tuple[str, int]], None] = FunctionSpy()
        self.getsockname_spy: FunctionSpy[Tuple[()], Tuple[str, int]] = FunctionSpy()
        self.listen_spy: FunctionSpy[Tuple[int], None] = FunctionSpy()
        self.recv_spy: FunctionSpy[Tuple[int], bytes] = FunctionSpy()
        self.recvfrom_spy: FunctionSpy[Tuple[int], Tuple[bytes, Optional[Tuple[str, int]]]] = FunctionSpy()
        self.sendall_spy: FunctionSpy[Tuple[bytes], int] = FunctionSpy()
        self.sendto_spy: FunctionSpy[Tuple[bytes, Tuple[str, int]], int] = FunctionSpy()
        self.setsockopt_spy: FunctionSpy[Tuple[int, int, Union[int, bytes]], None] = FunctionSpy()
        self.settimeout_spy: FunctionSpy[Tuple[float], None] = FunctionSpy()
        self.shutdown_spy: FunctionSpy[Tuple[int], None] = FunctionSpy()

    def __enter__(self) -> ISocket:
        return self.enter___spy(())

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType]
    ) -> None:
        return self.exit___spy((exc_type, exc_val, exc_tb))

    def accept(self) -> Tuple[ISocket, Tuple[str, int]]:
        return self.accept_spy(())

    def bind(self, address: Tuple[str, int]) -> None:
        self.bind_spy((address,))

    def close(self) -> None:
        self.close_spy(())

    def connect(self, address: Tuple[str, int]) -> None:
        self.connect_spy((address,))

    def getsockname(self) -> Tuple[str, int]:
        return self.getsockname_spy(())

    def listen(self, backlog: int) -> None:
        self.listen_spy((backlog,))

    def recv(self, bufsize: int) -> bytes:
        return self.recv_spy((bufsize,))

    def recvfrom(self, bufsize: int) -> Tuple[bytes, Optional[Tuple[str, int]]]:
        return self.recvfrom_spy((bufsize,))

    def sendall(self, data: bytes) -> None:
        self.sendall_spy((data,))

    def sendto(self, data: bytes, address: Tuple[str, int]) -> int:
        return self.sendto_spy((data, address))

    def setsockopt(self, level: int, optname: int, value: Union[int, bytes]) -> None:
        self.setsockopt_spy((level, optname, value))

    def settimeout(self, value: float) -> None:
        self.settimeout_spy((value,))

    def shutdown(self, how: int) -> None:
        self.shutdown_spy((how,))


class MockSocketFactory(ISocketFactory):
    @staticmethod
    def create_dummy(socket: ISocket) -> MockSocketFactory:
        mock = MockSocketFactory()
        mock.socket_spy.constant(socket)
        return mock

    def __init__(self) -> None:
        self.socket_spy: FunctionSpy[Tuple[int, int, int], ISocket] = FunctionSpy()

    def socket(self, family: int, type_: int, proto: int = -1) -> ISocket:
        return self.socket_spy((family, type_, proto))

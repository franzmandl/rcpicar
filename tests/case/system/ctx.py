from socket import AF_INET, IPPROTO_UDP, SOCK_DGRAM, SOCK_STREAM
from typing import Optional, Tuple
from rcpicar.client.Client import Client
from rcpicar.clock import IClock
from rcpicar.queue_ import IQueue
from rcpicar.server.Server import Server
from rcpicar.util.IdealQueue import IdealQueue
from tests.mock.gpio import MockGpio
from tests.mock.helper import mock_client_address, mock_server_address
from tests.mock.socket_ import MockSocket, MockSocketFactory


class Context:
    def __init__(self, clock: IClock) -> None:
        self.clock = clock
        self.tcp_client_to_server_queue: IQueue[bytes] = IdealQueue()
        self.tcp_server_to_client_queue: IQueue[bytes] = IdealQueue()
        self.udp_client_to_server_queue: IQueue[Tuple[bytes, Optional[Tuple[str, int]]]] = IdealQueue()
        self.udp_server_to_client_queue: IQueue[Tuple[bytes, Optional[Tuple[str, int]]]] = IdealQueue()
        self.broadcast_client_to_server_queue: IQueue[Tuple[bytes, Optional[Tuple[str, int]]]] = IdealQueue()
        self.broadcast_server_to_client_queue: IQueue[Tuple[bytes, Optional[Tuple[str, int]]]] = IdealQueue()


class ClientContext:
    def __init__(self, ctx: Context) -> None:
        self.client = Client()
        self.client.clock.set(ctx.clock)
        self.mock_socket_factory = MockSocketFactory()
        self.mock_socket_factory.socket_spy.mapping({
            (AF_INET, SOCK_STREAM, -1): MockSocket.create_tcp_client(
                mock_client_address, ctx.tcp_server_to_client_queue, ctx.tcp_client_to_server_queue),
            (AF_INET, SOCK_DGRAM, -1): MockSocket.create_udp_tunnel(
                mock_client_address, ctx.udp_server_to_client_queue, ctx.udp_client_to_server_queue),
            (AF_INET, SOCK_DGRAM, IPPROTO_UDP): MockSocket.create_udp_tunnel(
                mock_client_address, ctx.broadcast_server_to_client_queue, ctx.broadcast_client_to_server_queue),
        })
        self.client.socket_factory.set(self.mock_socket_factory)


class ServerContext:
    def __init__(self, ctx: Context) -> None:
        self.server = Server()
        self.server.clock.set(ctx.clock)
        self.mock_socket_factory = MockSocketFactory()
        self.mock_socket_factory.socket_spy.mapping({
            (AF_INET, SOCK_STREAM, -1): MockSocket.create_tcp_server(
                MockSocket.create_tcp_tunnel(
                    mock_server_address, ctx.tcp_client_to_server_queue, ctx.tcp_server_to_client_queue),
                mock_server_address, mock_server_address),
            (AF_INET, SOCK_DGRAM, -1): MockSocket.create_udp_server(
                mock_server_address, ctx.udp_client_to_server_queue, ctx.udp_server_to_client_queue),
            (AF_INET, SOCK_DGRAM, IPPROTO_UDP): MockSocket.create_udp_server(
                mock_server_address, ctx.broadcast_client_to_server_queue, ctx.broadcast_server_to_client_queue),
        })
        self.server.socket_factory.set(self.mock_socket_factory)
        self.gpio = MockGpio.create_dummy()
        self.server.gpio_factory.set(lambda: self.gpio)

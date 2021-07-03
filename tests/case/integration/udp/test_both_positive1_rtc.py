from socket import AF_INET, SOCK_DGRAM
from typing import Optional, Tuple
from rcpicar.queue_ import IQueue
from rcpicar.udp.UdpService import UdpService
from rcpicar.util.ConnectionDetails import ConnectionDetails
from rcpicar.util.IdealQueue import IdealQueue
from rcpicar.util.MultiServiceManager import MultiServiceManager
from rcpicar.util.Placeholder import Placeholder
from rcpicar.util.RTC import rtc
from tests.mock.helper import messages, mock_client_address, mock_server_address
from tests.mock.receive import MockReceiveListener
from tests.mock.socket_ import MockSocket, MockSocketFactory
from tests.mock.unreliable import MockUnreliableReceiveListener, MockUnreliableOsErrorListener


class Context:
    def __init__(self) -> None:
        self.client_to_server_queue: IQueue[Tuple[bytes, Optional[Tuple[str, int]]]] = IdealQueue()
        self.server_to_client_queue: IQueue[Tuple[bytes, Optional[Tuple[str, int]]]] = IdealQueue()
        self.mock_client_socket = MockSocket.create_udp_tunnel(
            mock_client_address, self.server_to_client_queue, self.client_to_server_queue)
        self.mock_client_socket_factory = MockSocketFactory.create_dummy(self.mock_client_socket)
        self.mock_server_socket = MockSocket.create_udp_server(
            mock_server_address, self.client_to_server_queue, self.server_to_client_queue)
        self.mock_server_socket_factory = MockSocketFactory.create_dummy(self.mock_server_socket)
        self.service_manager = MultiServiceManager()
        self.mock_client_receive_listener = MockReceiveListener.create_dummy()
        self.mock_client_unreliable_receive_listener = MockUnreliableReceiveListener.create_dummy()
        self.mock_client_unreliable_os_error_listener = MockUnreliableOsErrorListener.create_dummy()
        self.client_service = UdpService(
            rtc, False, Placeholder(mock_server_address), self.service_manager, self.mock_client_socket_factory)\
            .add_receive_listener(self.mock_client_receive_listener)\
            .add_unreliable_receive_listener(self.mock_client_unreliable_receive_listener)\
            .add_unreliable_os_error_listener(self.mock_client_unreliable_os_error_listener)
        self.mock_server_receive_listener = MockReceiveListener.create_dummy()
        self.mock_server_unreliable_receive_listener = MockUnreliableReceiveListener.create_dummy()
        self.mock_server_unreliable_os_error_listener = MockUnreliableOsErrorListener.create_dummy()
        self.server_service = UdpService(
            rtc, True, Placeholder(mock_client_address), self.service_manager, self.mock_server_socket_factory)\
            .add_receive_listener(self.mock_server_receive_listener)\
            .add_unreliable_receive_listener(self.mock_server_unreliable_receive_listener)\
            .add_unreliable_os_error_listener(self.mock_server_unreliable_os_error_listener)


def test() -> None:
    # given
    ctx = Context()
    # when
    with rtc.use_services(ctx.service_manager):
        ctx.mock_client_socket.recvfrom_spy.wait_for_call()
        ctx.mock_server_socket.recvfrom_spy.wait_for_call()
        ctx.client_service.send(messages[0])
        ctx.mock_server_socket.recvfrom_spy.wait_for_call()
        ctx.server_service.send(messages[1])
        ctx.mock_client_socket.recvfrom_spy.wait_for_call()
        ctx.client_service.send(messages[2])
        ctx.mock_server_socket.recvfrom_spy.wait_for_call()
        ctx.server_service.send(messages[3])
        ctx.mock_client_socket.recvfrom_spy.wait_for_call()
        ctx.client_service.send(messages[4])
        ctx.mock_server_socket.recvfrom_spy.wait_for_call()
        ctx.server_service.send(messages[5])
        ctx.mock_client_socket.recvfrom_spy.wait_for_call()
    # then
    assert ctx.mock_client_socket_factory.socket_spy.get_called_args() == [(AF_INET, SOCK_DGRAM, -1)]
    assert ctx.mock_client_socket.bind_spy.get_called_args() == []
    assert ctx.mock_client_receive_listener.on_receive_spy.get_called_args() == [
        (messages[1], ConnectionDetails(mock_client_address, mock_server_address)),
        (messages[3], ConnectionDetails(mock_client_address, mock_server_address)),
        (messages[5], ConnectionDetails(mock_client_address, mock_server_address)),
    ] == ctx.mock_client_unreliable_receive_listener.on_unreliable_receive_spy.get_called_args()
    assert ctx.mock_server_socket_factory.socket_spy.get_called_args() == [(AF_INET, SOCK_DGRAM, -1)]
    assert ctx.mock_server_socket.bind_spy.get_called_args() == [(mock_client_address,)]
    assert ctx.mock_server_receive_listener.on_receive_spy.get_called_args() == [
        (messages[0], ConnectionDetails(mock_server_address, mock_server_address)),
        (messages[2], ConnectionDetails(mock_server_address, mock_server_address)),
        (messages[4], ConnectionDetails(mock_server_address, mock_server_address)),
    ] == ctx.mock_server_unreliable_receive_listener.on_unreliable_receive_spy.get_called_args()


if __name__ == '__main__':
    test()

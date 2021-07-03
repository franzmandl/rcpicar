from socket import AF_INET, SOCK_STREAM
from rcpicar.tcp.TcpClientService import TcpClientService
from rcpicar.tcp.TcpServerService import TcpServerService
from rcpicar.queue_ import IQueue
from rcpicar.util.ConnectionDetails import ConnectionDetails
from rcpicar.util.IdealQueue import IdealQueue
from rcpicar.util.MultiServiceManager import MultiServiceManager
from rcpicar.util.Placeholder import Placeholder
from rcpicar.util.RTC import rtc
from tests.mock.helper import messages, mock_client_address, mock_server_address, mock_reconnect_seconds
from tests.mock.receive import MockReceiveListener
from tests.mock.reliable import MockReliableConnectListener, MockReliableDisconnectListener, MockReliableReceiveListener
from tests.mock.socket_ import MockSocket, MockSocketFactory


class Context:
    def __init__(self) -> None:
        self.client_to_server_queue: IQueue[bytes] = IdealQueue()
        self.server_to_client_queue: IQueue[bytes] = IdealQueue()
        self.mock_client_socket = MockSocket.create_tcp_client(
            mock_client_address, self.server_to_client_queue, self.client_to_server_queue)
        self.mock_client_socket_factory = MockSocketFactory.create_dummy(self.mock_client_socket)
        self.mock_server_socket_tunnel = MockSocket.create_tcp_tunnel(
            mock_server_address, self.client_to_server_queue, self.server_to_client_queue)
        self.mock_server_socket = MockSocket.create_tcp_server(
            self.mock_server_socket_tunnel, mock_server_address, mock_server_address)
        self.mock_server_socket_factory = MockSocketFactory.create_dummy(self.mock_server_socket)
        self.service_manager = MultiServiceManager()
        self.mock_client_receive_listener = MockReceiveListener.create_dummy()
        self.mock_client_reliable_connect_listener = MockReliableConnectListener.create_dummy()
        self.mock_client_reliable_disconnect_listener = MockReliableDisconnectListener.create_dummy()
        self.mock_client_reliable_receive_listener = MockReliableReceiveListener.create_dummy()
        self.client_service = TcpClientService(
            rtc, mock_reconnect_seconds,
            Placeholder(mock_server_address), self.service_manager, self.mock_client_socket_factory)\
            .add_receive_listener(self.mock_client_receive_listener)\
            .add_reliable_connect_listener(self.mock_client_reliable_connect_listener)\
            .add_reliable_disconnect_listener(self.mock_client_reliable_disconnect_listener)\
            .add_reliable_receive_listener(self.mock_client_reliable_receive_listener)
        self.mock_server_receive_listener = MockReceiveListener.create_dummy()
        self.mock_server_reliable_connect_listener = MockReliableConnectListener.create_dummy()
        self.mock_server_reliable_disconnect_listener = MockReliableDisconnectListener.create_dummy()
        self.mock_server_reliable_receive_listener = MockReliableReceiveListener.create_dummy()
        self.server_service = TcpServerService(
            mock_client_address, self.service_manager, self.mock_server_socket_factory)\
            .add_receive_listener(self.mock_server_receive_listener)\
            .add_reliable_connect_listener(self.mock_server_reliable_connect_listener)\
            .add_reliable_disconnect_listener(self.mock_server_reliable_disconnect_listener)\
            .add_reliable_receive_listener(self.mock_server_reliable_receive_listener)


def test() -> None:
    # given
    ctx = Context()
    # when
    with rtc.use_services(ctx.service_manager):
        ctx.mock_client_socket.recv_spy.wait_for_call()
        ctx.mock_server_socket_tunnel.recv_spy.wait_for_call()
        ctx.client_service.send(messages[0])
        ctx.mock_server_socket_tunnel.recv_spy.wait_for_call()
        ctx.server_service.send(messages[1])
        ctx.mock_client_socket.recv_spy.wait_for_call()
        ctx.client_service.send(messages[2])
        ctx.mock_server_socket_tunnel.recv_spy.wait_for_call()
        ctx.server_service.send(messages[3])
        ctx.mock_client_socket.recv_spy.wait_for_call()
        ctx.client_service.send(messages[4])
        ctx.mock_server_socket_tunnel.recv_spy.wait_for_call()
        ctx.server_service.send(messages[5])
        ctx.mock_client_socket.recv_spy.wait_for_call()
    ctx.mock_client_reliable_disconnect_listener.on_reliable_disconnect_spy.wait_for_call()
    ctx.mock_server_reliable_disconnect_listener.on_reliable_disconnect_spy.wait_for_call()
    # then
    assert ctx.mock_client_socket_factory.socket_spy.get_called_args() == [(AF_INET, SOCK_STREAM, -1)]
    assert ctx.mock_client_socket.connect_spy.get_called_args() == [(mock_server_address,)]
    assert ctx.mock_client_socket.getsockname_spy.get_called_args() == [()]
    assert ctx.mock_client_reliable_connect_listener.on_reliable_connect_spy.get_called_args() == [
        (ConnectionDetails(mock_client_address, mock_server_address),)]
    assert ctx.mock_client_socket.bind_spy.get_called_args() == []
    assert ctx.mock_client_receive_listener.on_receive_spy.get_called_args() == [
        (messages[1], ConnectionDetails(mock_client_address, mock_server_address)),
        (messages[3], ConnectionDetails(mock_client_address, mock_server_address)),
        (messages[5], ConnectionDetails(mock_client_address, mock_server_address)),
    ] == ctx.mock_client_reliable_receive_listener.on_reliable_receive_spy.get_called_args()
    assert ctx.mock_client_reliable_disconnect_listener.on_reliable_disconnect_spy.get_called_args() == [
        (ConnectionDetails(mock_client_address, mock_server_address),)]
    assert ctx.mock_server_socket_factory.socket_spy.get_called_args() == [(AF_INET, SOCK_STREAM, -1)]
    assert ctx.mock_server_socket.bind_spy.get_called_args() == [(mock_client_address,)]
    assert ctx.mock_server_socket.listen_spy.get_called_args() == [(1,)]
    assert ctx.mock_server_socket.accept_spy.get_called_args() == [()]
    assert ctx.mock_server_reliable_connect_listener.on_reliable_connect_spy.get_called_args() == [
        (ConnectionDetails(mock_server_address, mock_server_address),)]
    assert ctx.mock_server_receive_listener.on_receive_spy.get_called_args() == [
        (messages[0], ConnectionDetails(mock_server_address, mock_server_address)),
        (messages[2], ConnectionDetails(mock_server_address, mock_server_address)),
        (messages[4], ConnectionDetails(mock_server_address, mock_server_address)),
    ] == ctx.mock_server_reliable_receive_listener.on_reliable_receive_spy.get_called_args()
    assert ctx.mock_server_reliable_disconnect_listener.on_reliable_disconnect_spy.get_called_args() == [
        (ConnectionDetails(mock_server_address, mock_server_address),)]


if __name__ == '__main__':
    test()

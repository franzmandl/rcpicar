from __future__ import annotations
from logging import getLogger
from socket import AF_INET, SOCK_STREAM
from threading import Thread
from types import TracebackType
from typing import Optional, Tuple, Type
from ..constants import buffer_size
from ..log.util import log_method_call
from ..receive import IReceiveListener
from ..reliable import IReliableReceiveSendService, IReliableOsErrorListener, IReliableReceiveListener
from ..reliable import IReliableConnectListener, IReliableDisconnectListener
from ..service import IService, IServiceManager
from ..socket_ import ISocket, ISocketFactory
from ..util import checking
from ..util.ConnectionDetails import ConnectionDetails
from ..util.Listeners import Listeners
from ..util.Placeholder import Placeholder


class AcceptWrapper:
    def __init__(self, connection: Tuple[ISocket, Tuple[str, int]]) -> None:
        self.socket = connection[0]
        self.address = connection[1]

    def __enter__(self) -> Tuple[ISocket, Tuple[str, int]]:
        return self.socket.__enter__(), self.address

    def set_into_placeholder(self, placeholder: Placeholder[ISocket]) -> AcceptWrapper:
        placeholder.set(self.socket)
        return self

    def __exit__(
            self, exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType]
    ) -> None:
        self.socket.__exit__(exc_type, exc_val, exc_tb)


class TcpServerService(IService, IReliableReceiveSendService):
    def __init__(
            self,
            listen_address: Tuple[str, int],
            service_manager: IServiceManager,
            socket_factory: ISocketFactory,
    ) -> None:
        self.connected_listeners: Listeners[IReliableConnectListener] = Listeners()
        self.disconnected_listeners: Listeners[IReliableDisconnectListener] = Listeners()
        self.listen_address = listen_address
        self.logger = getLogger(__name__)
        self.os_error_listeners: Listeners[IReliableOsErrorListener] = Listeners()
        self.received_listeners: Listeners[IReceiveListener] = Listeners()
        self.reliable_received_listeners: Listeners[IReliableReceiveListener] = Listeners()
        self.should_run = True
        self.socket_factory = socket_factory
        self.server_socket: Placeholder[ISocket] = Placeholder()
        self.socket: Placeholder[ISocket] = Placeholder()
        self.thread = Thread(target=log_method_call(self.logger, self.run))
        service_manager.add_service(self)

    def add_reliable_connect_listener(self, listener: IReliableConnectListener) -> TcpServerService:
        self.connected_listeners.add_listener(listener)
        return self

    def add_reliable_disconnect_listener(self, listener: IReliableDisconnectListener) -> TcpServerService:
        self.disconnected_listeners.add_listener(listener)
        return self

    def add_receive_listener(self, listener: IReceiveListener) -> TcpServerService:
        self.received_listeners.add_listener(listener)
        return self

    def add_reliable_os_error_listener(self, listener: IReliableOsErrorListener) -> TcpServerService:
        self.os_error_listeners.add_listener(listener)
        return self

    def add_reliable_receive_listener(
            self,
            listener: IReliableReceiveListener
    ) -> TcpServerService:
        self.reliable_received_listeners.add_listener(listener)
        return self

    def get_service_name(self) -> str:
        return __name__

    def get_own_address(self) -> Tuple[str, int]:
        return self.listen_address

    def join_service(self, timeout_seconds: Optional[float] = None) -> bool:
        self.thread.join(timeout_seconds)
        return self.thread.is_alive()

    def run_connected_client(self, socket: ISocket, connection_details: ConnectionDetails) -> None:
        self.connected_listeners.for_each(
            lambda listener: listener.on_reliable_connect(connection_details))
        try:
            while self.should_run:
                message = socket.recv(buffer_size)
                if len(message) == 0:  # ... means that peer has gracefully shutdown connection
                    break
                self.received_listeners.for_each(
                    lambda listener: listener.on_receive(message, connection_details))
                self.reliable_received_listeners.for_each(
                    lambda listener: listener.on_reliable_receive(message, connection_details))
        except OSError as os_error:
            self.os_error_listeners.for_each(
                lambda listener: listener.on_reliable_os_error(os_error))
        finally:
            socket.shutdown_guaranteed()
            self.disconnected_listeners.for_each(
                lambda listener: listener.on_reliable_disconnect(connection_details))

    def run(self) -> None:
        with self.server_socket.set(self.socket_factory.socket(AF_INET, SOCK_STREAM)) as server_socket:
            server_socket.bind(self.listen_address)
            server_socket.listen(1)
            while self.should_run:
                try:
                    with AcceptWrapper(server_socket.accept()).set_into_placeholder(self.socket) as (
                            socket, client_address):
                        self.run_connected_client(socket, ConnectionDetails(socket.getsockname(), client_address))
                except OSError as os_error:
                    if self.should_run:
                        raise os_error
                if self.should_run:
                    self.socket.clear()

    def send(self, message: bytes) -> None:
        checking.check_message_length(len(message))
        self.socket.get().sendall(message)

    def start_service(self) -> None:
        self.thread.start()

    def stop_service(self) -> None:
        self.should_run = False
        socket = self.socket.get_optional()
        if socket is not None:
            socket.shutdown_guaranteed()
        server_socket = self.server_socket.get_optional_and_clear()
        if server_socket is not None:
            server_socket.shutdown_guaranteed()

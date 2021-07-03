from __future__ import annotations
from logging import getLogger
from socket import AF_INET, SOCK_STREAM
from threading import Thread
from typing import Optional, Tuple
from ..clock import IClock
from ..constants import buffer_size
from ..log.util import log_method_call
from ..receive import IReceiveListener
from ..reliable import IReliableReceiveListener, IReliableReceiveSendService, IReliableConnectListener
from ..reliable import IReliableDisconnectListener, IReliableOsErrorListener
from ..service import IService, IServiceManager
from ..socket_ import ISocket, ISocketFactory
from ..util import checking
from ..util.ConnectionDetails import ConnectionDetails
from ..util.InterruptableSleep import InterruptableSleep
from ..util.Listeners import Listeners
from ..util.Placeholder import Placeholder


class TcpClientService(IService, IReliableReceiveSendService):
    def __init__(
            self,
            clock: IClock,
            reconnect_seconds: float,
            server_address: Placeholder[Tuple[str, int]],
            service_manager: IServiceManager,
            socket_factory: ISocketFactory,
    ) -> None:
        self.connected_listeners: Listeners[IReliableConnectListener] = Listeners()
        self.disconnected_listeners: Listeners[IReliableDisconnectListener] = Listeners()
        self.interruptable_sleep = InterruptableSleep(clock)
        self.logger = getLogger(__name__)
        self.os_error_listeners: Listeners[IReliableOsErrorListener] = Listeners()
        self.received_listeners: Listeners[IReceiveListener] = Listeners()
        self.reconnect_seconds = reconnect_seconds
        self.reliable_received_listeners: Listeners[IReliableReceiveListener] = Listeners()
        self.server_address = server_address
        self.service_manager = service_manager
        self.should_run = True
        self.socket: Placeholder[ISocket] = Placeholder()
        self.socket_factory = socket_factory
        self.thread = Thread(target=log_method_call(self.logger, self.run))
        service_manager.add_service(self)

    def add_reliable_connect_listener(self, listener: IReliableConnectListener) -> TcpClientService:
        self.connected_listeners.add_listener(listener)
        return self

    def add_reliable_disconnect_listener(self, listener: IReliableDisconnectListener) -> TcpClientService:
        self.disconnected_listeners.add_listener(listener)
        return self

    def add_reliable_os_error_listener(self, listener: IReliableOsErrorListener) -> TcpClientService:
        self.os_error_listeners.add_listener(listener)
        return self

    def add_receive_listener(self, listener: IReceiveListener) -> TcpClientService:
        self.received_listeners.add_listener(listener)
        return self

    def add_reliable_receive_listener(
            self,
            listener: IReliableReceiveListener
    ) -> TcpClientService:
        self.reliable_received_listeners.add_listener(listener)
        return self

    def get_service_name(self) -> str:
        return __name__

    def get_own_address(self) -> Tuple[str, int]:
        return self.socket.get().getsockname()

    def join_service(self, timeout_seconds: Optional[float] = None) -> bool:
        self.thread.join(timeout_seconds)
        return self.thread.is_alive()

    def run_with_server_address(self, server_address: Tuple[str, int]) -> None:
        while self.should_run:
            try:
                with self.socket.set(self.socket_factory.socket(AF_INET, SOCK_STREAM)) as socket:
                    socket.connect(server_address)
                    connection_details = ConnectionDetails(socket.getsockname(), server_address)
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
                    finally:
                        self.disconnected_listeners.for_each(
                            lambda listener: listener.on_reliable_disconnect(connection_details))
            except OSError as os_error:
                # Is thrown if connection could not be established or got lost
                self.os_error_listeners.for_each(lambda listener: listener.on_reliable_os_error(os_error))
            if self.should_run:
                self.socket.clear()
                self.interruptable_sleep.sleep(self.reconnect_seconds)

    def run(self) -> None:
        server_address = self.server_address.get_eventually(self.service_manager).get_blocking()
        if server_address is not None:
            self.run_with_server_address(server_address)

    def send(self, message: bytes) -> None:
        checking.check_message_length(len(message))
        self.socket.get().sendall(message)

    def start_service(self) -> None:
        self.thread.start()

    def stop_service(self) -> None:
        self.should_run = False
        self.interruptable_sleep.interrupt()
        socket = self.socket.get_optional_and_clear()
        if socket is not None:
            socket.shutdown_guaranteed(
                lambda os_error: self.logger.info(
                    'TCP socket was already shutdown or connection was never established.'))

from __future__ import annotations
from logging import getLogger
from math import inf
from socket import AF_INET, SOCK_DGRAM
from threading import Thread
from typing import Optional, Tuple
from ..clock import IClock
from ..constants import buffer_size
from ..log.util import log_method_call
from ..receive import IReceiveListener
from ..service import IService, IServiceManager
from ..socket_ import ISocket, ISocketFactory
from ..unreliable import IUnreliableOsErrorListener, IUnreliableReceiveListener, IUnreliableReceiveSendService
from ..util import checking
from ..util.ConnectionDetails import ConnectionDetails
from ..util.Listeners import Listeners
from ..util.Placeholder import Placeholder


class UdpService(IService, IUnreliableReceiveSendService):
    def __init__(
            self,
            clock: IClock,
            is_server: bool,
            server_address: Placeholder[Tuple[str, int]],
            service_manager: IServiceManager,
            socket_factory: ISocketFactory,
            unreliable_timeout_seconds: float = inf,
    ) -> None:
        logger = getLogger(__name__)
        self.clock = clock
        self.is_server = is_server
        self.os_error_listeners: Listeners[IUnreliableOsErrorListener] = Listeners()
        self.receiver_address: Optional[Tuple[str, int]] = None
        self.last_received_seconds = -inf
        self.received_listeners: Listeners[IReceiveListener] = Listeners()
        self.server_address = server_address
        self.service_manager = service_manager
        self.should_run = True
        self.socket: Placeholder[ISocket] = Placeholder()
        self.socket_factory = socket_factory
        self.thread = Thread(target=log_method_call(logger, self.run))
        self.unreliable_received_listeners: Listeners[IUnreliableReceiveListener] = Listeners()
        self.unreliable_timeout_seconds = unreliable_timeout_seconds
        service_manager.add_service(self)

    def add_unreliable_os_error_listener(self, listener: IUnreliableOsErrorListener) -> UdpService:
        self.os_error_listeners.add_listener(listener)
        return self

    def add_receive_listener(self, listener: IReceiveListener) -> UdpService:
        self.received_listeners.add_listener(listener)
        return self

    def add_unreliable_receive_listener(
            self,
            listener: IUnreliableReceiveListener
    ) -> UdpService:
        self.unreliable_received_listeners.add_listener(listener)
        return self

    def get_service_name(self) -> str:
        return __name__

    def join_service(self, timeout_seconds: Optional[float] = None) -> bool:
        self.thread.join(timeout_seconds)
        return self.thread.is_alive()

    def run(self) -> None:
        with self.socket.set(self.socket_factory.socket(AF_INET, SOCK_DGRAM)) as socket:
            server_address = self.server_address.get_eventually(self.service_manager).get_blocking()
            if server_address is None:
                return
            if self.is_server:
                socket.bind(server_address)
            else:
                self.receiver_address = server_address

            while self.should_run:
                try:
                    (message, receiver_address) = socket.recvfrom(buffer_size)
                    if receiver_address is None:
                        break
                    self.last_received_seconds = self.clock.get_seconds()
                    connection_details = ConnectionDetails(socket.getsockname(), receiver_address)
                    self.receiver_address = receiver_address
                    self.received_listeners.for_each(
                        lambda listener: listener.on_receive(message, connection_details))
                    self.unreliable_received_listeners.for_each(
                        lambda listener: listener.on_unreliable_receive(message, connection_details))
                except OSError as os_error:
                    self.os_error_listeners.for_each(
                        lambda listener: listener.on_unreliable_os_error(os_error))

    def send(self, message: bytes) -> None:
        checking.check_message_length(len(message))
        receiver_address = self.receiver_address
        if receiver_address is None:
            return
        if self.last_received_seconds + self.unreliable_timeout_seconds < self.clock.get_seconds():
            return
        socket = self.socket.get_optional()
        if socket is not None:
            socket.sendto(message, receiver_address)

    def start_service(self) -> None:
        self.thread.start()

    def stop_service(self) -> None:
        self.should_run = False
        socket = self.socket.get_optional_and_clear()
        if socket is not None:
            socket.shutdown_guaranteed()

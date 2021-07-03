from logging import getLogger
from socket import AF_INET, IPPROTO_UDP, SO_BROADCAST, SOCK_DGRAM, SOL_SOCKET
try:
    from socket import SO_REUSEPORT

    socket_can_reuse_port = True
except ImportError:
    SO_REUSEPORT = 0
    socket_can_reuse_port = False
from threading import Thread
from typing import Optional
from .DiscoveryCommonArguments import DiscoveryCommonArguments
from .DiscoveryRequestMessage import DiscoveryRequestMessage
from .DiscoveryResponseMessage import DiscoveryResponseMessage
from ..constants import buffer_size
from ..log.util import log_method_call
from ..service import IService, IServiceManager
from ..socket_ import ISocket, ISocketFactory
from ..util.argument import IArguments
from ..util.Placeholder import Placeholder


class DiscoveryServerArguments(IArguments):
    def __init__(self) -> None:
        self.common = DiscoveryCommonArguments()


class DiscoveryServerService(IService):
    def __init__(
            self,
            arguments: DiscoveryServerArguments,
            listen_port: int,
            socket_factory: ISocketFactory,
            service_manager: IServiceManager
    ) -> None:
        logger = getLogger(__name__)
        self.arguments = arguments
        self.listen_port = listen_port
        self.should_run = True
        self.socket: Placeholder[ISocket] = Placeholder()
        self.socket_factory = socket_factory
        self.thread = Thread(target=log_method_call(logger, self.run))
        service_manager.add_service(self)

    def get_service_name(self) -> str:
        return __name__

    def join_service(self, timeout_seconds: Optional[float] = None) -> bool:
        self.thread.join(timeout_seconds)
        return self.thread.is_alive()

    def run(self) -> None:
        with self.socket.set(self.socket_factory.socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) as socket:
            socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            if socket_can_reuse_port:
                socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
            socket.bind(('', self.arguments.common.port.get()))
            while self.should_run:
                message, address = socket.recvfrom(buffer_size)
                if address is not None and DiscoveryRequestMessage.is_valid(message):
                    response = DiscoveryResponseMessage(self.listen_port)
                    socket.sendto(response.encode(), address)

    def start_service(self) -> None:
        self.thread.start()

    def stop_service(self) -> None:
        self.should_run = False
        socket = self.socket.get_optional_and_clear()
        if socket is not None:
            socket.shutdown_guaranteed()

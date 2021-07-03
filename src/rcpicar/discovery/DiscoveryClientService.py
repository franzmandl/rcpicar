from logging import getLogger
from socket import AF_INET, IPPROTO_UDP, SO_BROADCAST, SOCK_DGRAM, SOL_SOCKET, timeout
try:
    from socket import SO_REUSEPORT

    socket_can_reuse_port = True
except ImportError:
    SO_REUSEPORT = 0
    socket_can_reuse_port = False
from threading import Thread
from typing import Optional, Tuple
from .DiscoveryCommonArguments import DiscoveryCommonArguments
from .DiscoveryRequestMessage import DiscoveryRequestMessage
from .DiscoveryResponseMessage import DiscoveryResponseMessage
from .interfaces import IDiscoveryClientService
from ..constants import buffer_size
from ..log.util import log_method_call
from ..service import IService, IServiceManager
from ..socket_ import ISocket, ISocketFactory
from ..util.argument import AnyArguments, create_value_argument, IArguments
from ..util.Lazy import Lazy
from ..util.Placeholder import Placeholder


class DiscoveryClientArguments(IArguments):
    def __init__(self) -> None:
        self.common = DiscoveryCommonArguments()
        self.ip = Lazy(lambda store: '255.255.255.255')
        self.address = Lazy(lambda store: (self.ip(store), self.common.port(store)))
        self.timeout_seconds = Lazy(lambda store: 2)

    def get_arguments(self) -> AnyArguments:
        return [
            create_value_argument(
                self.timeout_seconds, '--discovery-timeout-seconds', int,
                'Retry discovery after this amount of seconds.'),
            create_value_argument(self.ip, '--discovery-ip', str, 'Where to send discovery broadcast.'),
        ]


class DiscoveryClientService(IDiscoveryClientService, IService):
    def __init__(
            self,
            arguments: DiscoveryClientArguments,
            service_manager: IServiceManager,
            socket_factory: ISocketFactory,
    ) -> None:
        self.arguments = arguments
        self.logger = getLogger(__name__)
        self.server_address: Placeholder[Tuple[str, int]] = Placeholder()
        self.should_run = True
        self.socket: Placeholder[ISocket] = Placeholder()
        self.socket_factory = socket_factory
        self.thread = Thread(target=log_method_call(self.logger, self.run))
        service_manager.add_service(self)

    def get_server_address(self) -> Placeholder[Tuple[str, int]]:
        return self.server_address

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
            socket.settimeout(self.arguments.timeout_seconds.get())
            while self.should_run:
                try:
                    socket.sendto(DiscoveryRequestMessage.encode(), self.arguments.address.get())
                    message, address = socket.recvfrom(buffer_size)
                    if address is not None and DiscoveryResponseMessage.is_valid(message):
                        self.stop_service()
                        response = DiscoveryResponseMessage.decode(message)
                        self.server_address.set((address[0], response.port))
                except timeout:
                    self.logger.warning('timeout')
                except OSError as os_error:
                    if self.should_run:
                        raise os_error

    def start_service(self) -> None:
        self.thread.start()

    def stop_service(self) -> None:
        self.should_run = False
        socket = self.socket.get_optional_and_clear()
        if socket is not None:
            socket.shutdown_guaranteed()

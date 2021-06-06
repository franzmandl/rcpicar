from socket import socket
from typing import Tuple
from .ClientArguments import ClientArguments
from ..car.CarClientService import CarClientArguments, CarClientService
from ..clock import IClock
from ..constants import discover_server_ip
from ..discovery.DiscoveryClientService import DiscoveryClientArguments, DiscoveryClientService
from ..gstreamer.GStreamerClientService import GStreamerClientArguments, GStreamerClientService
from ..latency.LatencyClientService import LatencyClientService
from ..log.LogArguments import LogArguments
from ..reliable import IReliableReceiveSendService
from ..routed.RoutedSendService import RoutedSendService
from ..routed.RoutedReceiveService import RoutedReceiveService
from ..service import AbstractServiceManager
from ..socket_ import ISocketFactory
from ..tcp.TcpClientService import TcpClientService
from ..udp.UdpService import UdpService
from ..unreliable import IUnreliableReceiveSendService
from ..util.Lazy import Lazy
from ..util.MultiServiceManager import MultiServiceManager
from ..util.Placeholder import Placeholder
from ..util.RTC import rtc
from ..util.Socket import SocketFactory


class Client:
    def __init__(self) -> None:
        self.car_arguments = CarClientArguments()
        self.client_arguments = ClientArguments()
        self.discovery_arguments = DiscoveryClientArguments()
        self.gstreamer_arguments = GStreamerClientArguments()
        self.log_arguments = LogArguments()
        self.clock: Lazy[IClock] = Lazy(lambda store: rtc)
        self.socket_factory: Lazy[ISocketFactory] = Lazy(lambda store: SocketFactory(socket))
        self.service_manager: Lazy[AbstractServiceManager] = Lazy(lambda store: MultiServiceManager(self.clock(store)))
        self.discovery_service = Lazy(lambda store: DiscoveryClientService(
            self.discovery_arguments, self.service_manager(store), self.socket_factory(store)))

        def create_server_address(store: bool) -> Placeholder[Tuple[str, int]]:
            if self.client_arguments.server_address(store)[0] == discover_server_ip:
                return self.discovery_service(store).server_address
            else:
                return Placeholder(self.client_arguments.server_address(store))

        self.server_address = Lazy(create_server_address)
        self.reliable_service: Lazy[IReliableReceiveSendService] = Lazy(lambda store: TcpClientService(
            self.clock(store), self.client_arguments.reconnect_seconds(store), self.server_address(store),
            self.service_manager(store), self.socket_factory(store)))
        self.unreliable_service: Lazy[IUnreliableReceiveSendService] = Lazy(lambda store: UdpService(
            self.clock(store), False, self.server_address(store), self.service_manager(store),
            self.socket_factory(store)))
        self.reliable_routed_receive_service = Lazy(lambda store: RoutedReceiveService(
            self.reliable_service(store)))
        self.reliable_routed_send_service = Lazy(lambda store: RoutedSendService(self.reliable_service(store)))
        self.unreliable_routed_receive_service = Lazy(lambda store: RoutedReceiveService(
            self.unreliable_service(store)))
        self.unreliable_routed_send_service = Lazy(lambda store: RoutedSendService(self.unreliable_service(store)))
        self.car_service = Lazy(lambda store: CarClientService(
            self.car_arguments, self.clock(store), self.reliable_service(store),
            self.unreliable_routed_send_service(store), self.service_manager(store)))
        self.gstreamer_service = Lazy(lambda store: GStreamerClientService(
            self.gstreamer_arguments, self.reliable_routed_receive_service(store),
            self.reliable_routed_send_service(store)))
        self.latency_service = Lazy(lambda store: LatencyClientService(
            self.unreliable_routed_receive_service(store), self.unreliable_routed_send_service(store)))

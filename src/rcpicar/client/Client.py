from socket import socket
from typing import ContextManager, Tuple
from .ClientArguments import ClientArguments
from ..car.CarClientService import CarClientService
from ..clock import IClock
from ..constants import discover_server_ip
from ..discovery.DiscoveryClientService import DiscoveryClientArguments, DiscoveryClientService
from ..discovery.interfaces import IDiscoveryClientService
from ..expire.ExpireSendService import ExpireSendService
from ..gpio.interfaces import IGpioService
from ..gstreamer.GStreamerClientService import GStreamerClientArguments, GStreamerClientService
from ..gstreamer.interfaces import IGStreamerClientService
from ..latency.LatencyClientService import LatencyClientService
from ..log.LogArguments import LogArguments
from ..message import message_types
from ..priority.PrioritySendService import PrioritySendService
from ..receive import IReceiveService
from ..reliable import IReliableReceiveSendService
from ..routed.interfaces import IRoutedReceiveService, IRoutedSendService
from ..routed.RoutedSendService import RoutedSendService
from ..routed.RoutedReceiveService import RoutedReceiveService
from ..send import ISendService
from ..service import IServiceManager
from ..socket_ import ISocketFactory
from ..tcp.TcpClientService import TcpClientService
from ..timeout.interfaces import ITimeoutSendService
from ..timeout.TimeoutSendService import TimeoutSendService
from ..udp.UdpService import UdpService
from ..unreliable import IUnreliableReceiveSendService
from ..util.Lazy import Lazy
from ..util.MultiServiceManager import MultiServiceManager
from ..util.Placeholder import Placeholder
from ..util.RTC import rtc
from ..util.Socket import SocketFactory


class Client:
    def __init__(self) -> None:
        self.client_arguments = ClientArguments()
        self.discovery_arguments = DiscoveryClientArguments()
        self.gstreamer_arguments = GStreamerClientArguments()
        self.log_arguments = LogArguments()

        self.clock: Lazy[IClock] = Lazy(lambda store: rtc)
        self.socket_factory: Lazy[ISocketFactory] = Lazy(lambda store: SocketFactory(socket))

        self.multi_service_manager = Lazy(lambda store: MultiServiceManager())
        self.service_manager: Lazy[IServiceManager] = Lazy(lambda store: self.multi_service_manager(store))

        self.discovery_service_implementation = Lazy(lambda store: DiscoveryClientService(
            self.discovery_arguments, self.service_manager(store), self.socket_factory(store)))
        self.discovery_service: Lazy[IDiscoveryClientService] = Lazy(
            lambda store: self.discovery_service_implementation(store))

        def create_server_address(store: bool) -> Placeholder[Tuple[str, int]]:
            if self.client_arguments.server_address(store)[0] == discover_server_ip:
                return self.discovery_service(store).get_server_address()
            else:
                return Placeholder(self.client_arguments.server_address(store))

        self.server_address = Lazy(create_server_address)

        self.tcp_service = Lazy(lambda store: TcpClientService(
            self.clock(store), self.client_arguments.reconnect_seconds(store), self.server_address(store),
            self.service_manager(store), self.socket_factory(store)))
        self.reliable_service: Lazy[IReliableReceiveSendService] = Lazy(lambda store: self.tcp_service(store))

        self.udp_service = Lazy(lambda store: UdpService(
            self.clock(store), False, self.server_address(store), self.service_manager(store),
            self.socket_factory(store)))
        self.unreliable_service: Lazy[IUnreliableReceiveSendService] = Lazy(lambda store: self.udp_service(store))

        self.reliable_routed_receive_service: Lazy[IRoutedReceiveService] = Lazy(lambda store: RoutedReceiveService(
            self.reliable_service(store)))
        self.reliable_routed_send_service: Lazy[IRoutedSendService] = Lazy(lambda store: RoutedSendService(
            self.reliable_service(store)))
        self.unreliable_routed_receive_service: Lazy[IRoutedReceiveService] = Lazy(lambda store: RoutedReceiveService(
            self.unreliable_service(store)))
        self.unreliable_routed_send_service: Lazy[IRoutedSendService] = Lazy(lambda store: RoutedSendService(
            self.unreliable_service(store)))

        self.car_send_service: Lazy[ISendService] = Lazy(
            lambda store: self.unreliable_routed_send_service(store).create_send_service(message_types.car))

        self.priority_service_implementation = Lazy(lambda store: PrioritySendService(
            self.client_arguments.priority(store), self.car_send_service(store)))
        self.priority_service: Lazy[ISendService] = Lazy(lambda store: self.priority_service_implementation(store))

        self.expire_service_implementation = Lazy(lambda store: ExpireSendService(self.priority_service(store)))
        self.expire_service: Lazy[ISendService] = Lazy(lambda store: self.expire_service_implementation(store))

        self.timeout_service_implementation = Lazy(lambda store: TimeoutSendService(
            self.clock(store), self.expire_service(store), self.service_manager(store),
            self.client_arguments.send_timeout_seconds(store)))
        self.timeout_service: Lazy[ITimeoutSendService] = Lazy(lambda store: self.timeout_service_implementation(store))

        self.car_service_implementation = Lazy(lambda store: CarClientService(
            self.reliable_service(store), self.timeout_service(store)))
        self.car_service: Lazy[IGpioService] = Lazy(lambda store: self.car_service_implementation(store))

        self.gstreamer_receive_service: Lazy[IReceiveService] = Lazy(
            lambda store: self.reliable_routed_receive_service(store).create_receive_service(message_types.gstreamer))
        self.gstreamer_send_service: Lazy[ISendService] = Lazy(
            lambda store: self.reliable_routed_send_service(store).create_send_service(message_types.gstreamer))
        self.gstreamer_service_implementation = Lazy(lambda store: GStreamerClientService(
            self.gstreamer_arguments, self.gstreamer_receive_service(store), self.gstreamer_send_service(store)))
        self.gstreamer_service: Lazy[IGStreamerClientService] = Lazy(
            lambda store: self.gstreamer_service_implementation(store))

        self.latency_receive_service: Lazy[IReceiveService] = Lazy(
            lambda store: self.unreliable_routed_receive_service(store).create_receive_service(message_types.latency))
        self.latency_send_service: Lazy[ISendService] = Lazy(
            lambda store: self.unreliable_routed_send_service(store).create_send_service(message_types.latency))
        self.latency_service = Lazy(lambda store: LatencyClientService(
            self.latency_receive_service(store), self.latency_send_service(store)))

    def use_services(self) -> ContextManager[None]:
        return self.clock.get().use_services(self.service_manager.get())

from socket import socket
from typing import Callable, ContextManager
from .ServerArguments import ServerArguments
from ..car.CarServerService import CarServerService
from ..clock import IClock
from ..discovery.DiscoveryServerService import DiscoveryServerArguments, DiscoveryServerService
from ..expire.ExpireReceiveService import ExpireReceiveService
from ..expire.interfaces import IExpireReceiveService
from ..gpio.GpioServerService import GpioServerArguments, GpioServerService
from ..gpio.interfaces import IGpio, IGpioService
from ..gpio.PiGpio import PiGpio
from ..gstreamer.GStreamerServerService import GStreamerServerArguments, GStreamerServerService
from ..latency.interfaces import ILatencyServerService
from ..latency.LatencyServerService import LatencyServerArguments, LatencyServerService
from ..log.LogArguments import LogArguments
from ..message import message_types
from ..priority.PriorityReceiveService import PriorityReceiveService
from ..process import ProcessFactory
from ..receive import IReceiveService
from ..reliable import IReliableReceiveSendService
from ..routed.interfaces import IRoutedReceiveService, IRoutedSendService
from ..routed.RoutedSendService import RoutedSendService
from ..routed.RoutedReceiveService import RoutedReceiveService
from ..send import ISendService
from ..service import IServiceManager
from ..socket_ import ISocketFactory
from ..stop.interfaces import IStopServerService
from ..stop.StopServerService import StopServerService
from ..tcp.TcpServerService import TcpServerService
from ..throttle.ThrottleServerService import ThrottleServerArguments, ThrottleServerService
from ..timeout.interfaces import ITimeoutReceiveService
from ..timeout.TimeoutReceiveService import TimeoutReceiveService
from ..udp.UdpService import UdpService
from ..unreliable import IUnreliableReceiveSendService
from ..util.Lazy import Lazy
from ..util.MultiServiceManager import MultiServiceManager
from ..util.Placeholder import Placeholder
from ..util.Process import Process
from ..util.RTC import rtc
from ..util.Socket import SocketFactory


class Server:
    def __init__(self) -> None:
        self.discovery_arguments = DiscoveryServerArguments()
        self.gpio_arguments = GpioServerArguments()
        self.gstreamer_arguments = GStreamerServerArguments()
        self.latency_arguments = LatencyServerArguments()
        self.log_arguments = LogArguments()
        self.server_arguments = ServerArguments()
        self.throttle_arguments = ThrottleServerArguments()

        self.clock: Lazy[IClock] = Lazy(lambda store: rtc)
        self.process_factory: Lazy[ProcessFactory] = Lazy(lambda store: Process)
        self.socket_factory: Lazy[ISocketFactory] = Lazy(lambda store: SocketFactory(socket))
        self.gpio_factory: Lazy[Callable[[], IGpio]] = Lazy(lambda store: PiGpio)

        self.multi_service_manager = Lazy(lambda store: MultiServiceManager())
        self.service_manager: Lazy[IServiceManager] = Lazy(lambda store: self.multi_service_manager(store))

        self.discovery_service = Lazy(lambda store: DiscoveryServerService(
            self.discovery_arguments, self.server_arguments.listen_address(store)[1],
            self.socket_factory(store), self.service_manager(store)))

        self.gpio_service_implementation = Lazy(lambda store: GpioServerService(
            self.gpio_arguments, self.gpio_factory(store), self.service_manager(store)))
        self.gpio_service: Lazy[IGpioService] = Lazy(lambda store: self.gpio_service_implementation(store))

        self.tcp_service = Lazy(lambda store: TcpServerService(
            self.server_arguments.listen_address(store), self.service_manager(store), self.socket_factory(store)))
        self.reliable_service: Lazy[IReliableReceiveSendService] = Lazy(lambda store: self.tcp_service(store))

        self.udp_service = Lazy(lambda store: UdpService(
            self.clock(store), True, Placeholder(self.server_arguments.listen_address(store)),
            self.service_manager(store), self.socket_factory(store),
            self.server_arguments.unreliable_timeout_seconds(store)))
        self.unreliable_service: Lazy[IUnreliableReceiveSendService] = Lazy(lambda store: self.udp_service(store))

        self.reliable_routed_receive_service: Lazy[IRoutedReceiveService] = Lazy(lambda store: RoutedReceiveService(
            self.reliable_service(store)))
        self.reliable_routed_send_service: Lazy[IRoutedSendService] = Lazy(lambda store: RoutedSendService(
            self.reliable_service(store)))
        self.unreliable_routed_receive_service: Lazy[IRoutedReceiveService] = Lazy(lambda store: RoutedReceiveService(
            self.unreliable_service(store)))
        self.unreliable_routed_send_service: Lazy[IRoutedSendService] = Lazy(lambda store: RoutedSendService(
            self.unreliable_service(store)))

        self.latency_receive_service: Lazy[IReceiveService] = Lazy(
            lambda store: self.unreliable_routed_receive_service(store).create_receive_service(message_types.latency))
        self.latency_send_service: Lazy[ISendService] = Lazy(
            lambda store: self.unreliable_routed_send_service(store).create_send_service(message_types.latency))
        self.latency_service_implementation = Lazy(lambda store: LatencyServerService(
            self.latency_arguments, self.clock(store), self.latency_receive_service(store),
            self.latency_send_service(store), self.service_manager(store)))
        self.latency_service: Lazy[ILatencyServerService] = Lazy(
            lambda store: self.latency_service_implementation(store))

        self.car_receive_service: Lazy[IReceiveService] = Lazy(
            lambda store: self.unreliable_routed_receive_service(store).create_receive_service(message_types.car))

        self.priority_service_implementation = Lazy(lambda store: PriorityReceiveService(
            self.clock(store), self.car_receive_service(store), self.service_manager(store),
            self.server_arguments.priority_timeout_seconds(store)))
        self.priority_service: Lazy[IReceiveService] = Lazy(lambda store: self.priority_service_implementation(store))

        self.expire_service_implementation = Lazy(lambda store: ExpireReceiveService(self.priority_service(store)))
        self.expire_service: Lazy[IExpireReceiveService] = Lazy(lambda store: self.expire_service_implementation(store))

        self.timeout_service_implementation = Lazy(lambda store: TimeoutReceiveService(
            self.clock(store), self.expire_service(store), self.service_manager(store)))
        self.timeout_service: Lazy[ITimeoutReceiveService] = Lazy(
            lambda store: self.timeout_service_implementation(store))

        self.throttle_service_implementation = Lazy(lambda store: ThrottleServerService(
            self.throttle_arguments, self.gpio_service(store), self.latency_service(store),
            self.timeout_service(store)))
        self.throttle_service: Lazy[IGpioService] = Lazy(lambda store: self.throttle_service_implementation(store))

        self.car_service = Lazy(lambda store: CarServerService(
            self.expire_service(store), self.throttle_service(store), self.reliable_service(store),
            self.timeout_service(store)))

        self.gstreamer_receive_service: Lazy[IReceiveService] = Lazy(
            lambda store: self.reliable_routed_receive_service(store).create_receive_service(message_types.gstreamer))
        self.gstreamer_send_service: Lazy[ISendService] = Lazy(
            lambda store: self.reliable_routed_send_service(store).create_send_service(message_types.gstreamer))
        self.gstreamer_service = Lazy(lambda store: GStreamerServerService(
            self.gstreamer_arguments, self.process_factory(store), self.gstreamer_receive_service(store),
            self.reliable_service(store), self.gstreamer_send_service(store), self.service_manager(store)))

        self.stop_receive_service: Lazy[IReceiveService] = Lazy(
            lambda store: self.reliable_routed_receive_service(store).create_receive_service(message_types.stop))
        self.stop_service_implementation = Lazy(lambda store: StopServerService(
            self.stop_receive_service(store), self.service_manager(store)))
        self.stop_service: Lazy[IStopServerService] = Lazy(lambda store: self.stop_service_implementation(store))

    def use_services(self) -> ContextManager[None]:
        return self.clock.get().use_services(self.service_manager.get())

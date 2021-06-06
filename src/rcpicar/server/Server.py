from socket import socket
from typing import Callable
from .ServerArguments import ServerArguments
from ..car.CarServerService import CarServerArguments, CarServerService
from ..clock import IClock
from ..discovery.DiscoveryServerService import DiscoveryServerArguments, DiscoveryServerService
from ..gpio.GpioServerService import GpioServerArguments, GpioServerService
from ..gpio.IGpio import IGpio
from ..gpio.IGpioServerService import IGpioServerService
from ..gpio.PiGpio import PiGpio
from ..gstreamer.GStreamerServerService import GStreamerServerArguments, GStreamerServerService
from ..latency.LatencyServerService import LatencyServerArguments, LatencyServerService
from ..log.LogArguments import LogArguments
from ..process import ProcessFactory
from ..reliable import IReliableReceiveSendService
from ..routed.RoutedSendService import RoutedSendService
from ..routed.RoutedReceiveService import RoutedReceiveService
from ..service import AbstractServiceManager
from ..socket_ import ISocketFactory
from ..stop.StopServerService import StopServerService
from ..tcp.TcpServerService import TcpServerService
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
        self.car_arguments = CarServerArguments()
        self.discovery_arguments = DiscoveryServerArguments()
        self.gpio_arguments = GpioServerArguments()
        self.gstreamer_arguments = GStreamerServerArguments()
        self.latency_arguments = LatencyServerArguments()
        self.log_arguments = LogArguments()
        self.server_arguments = ServerArguments()
        self.clock: Lazy[IClock] = Lazy(lambda store: rtc)
        self.process_factory: Lazy[ProcessFactory] = Lazy(lambda store: Process)
        self.socket_factory: Lazy[ISocketFactory] = Lazy(lambda store: SocketFactory(socket))
        self.service_manager: Lazy[AbstractServiceManager] = Lazy(lambda store: MultiServiceManager(self.clock(store)))
        self.discovery_service = Lazy(lambda store: DiscoveryServerService(
            self.discovery_arguments, self.server_arguments.listen_address(store)[1],
            self.socket_factory(store), self.service_manager(store)))
        self.gpio_factory: Lazy[Callable[[], IGpio]] = Lazy(lambda store: PiGpio)
        self.gpio_service: Lazy[IGpioServerService] = Lazy(lambda store: GpioServerService(
            self.gpio_arguments, self.gpio_factory(store), self.service_manager(store)))
        self.reliable_service: Lazy[IReliableReceiveSendService] = Lazy(lambda store: TcpServerService(
            self.server_arguments.listen_address(store), self.service_manager(store), self.socket_factory(store)))
        self.unreliable_service: Lazy[IUnreliableReceiveSendService] = Lazy(lambda store: UdpService(
            self.clock(store), True, Placeholder(self.server_arguments.listen_address(store)),
            self.service_manager(store), self.socket_factory(store),
            self.server_arguments.unreliable_timeout_seconds(store)))
        self.reliable_routed_receive_service = Lazy(lambda store: RoutedReceiveService(self.reliable_service(store)))
        self.reliable_routed_send_service = Lazy(lambda store: RoutedSendService(self.reliable_service(store)))
        self.unreliable_routed_receive_service = Lazy(lambda store: RoutedReceiveService(
            self.unreliable_service(store)))
        self.unreliable_routed_send_service = Lazy(lambda store: RoutedSendService(self.unreliable_service(store)))
        self.latency_service = Lazy(lambda store: LatencyServerService(
            self.latency_arguments, self.clock(store), self.unreliable_routed_receive_service(store),
            self.unreliable_routed_send_service(store), self.service_manager(store)))
        self.car_service = Lazy(lambda store: CarServerService(
            self.car_arguments, self.clock(store), self.gpio_service(store), self.latency_service(store),
            self.reliable_service(store), self.unreliable_routed_receive_service(store), self.service_manager(store)))
        self.gstreamer_service = Lazy(lambda store: GStreamerServerService(
            self.gstreamer_arguments, self.process_factory(store), self.reliable_routed_receive_service(store),
            self.reliable_service(store), self.reliable_routed_send_service(store), self.service_manager(store)))
        self.stop_service = Lazy(lambda store: StopServerService(
            self.reliable_routed_receive_service(store), self.service_manager(store)))

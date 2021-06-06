from __future__ import annotations
from logging import getLogger
from .CarMessage import CarMessage
from .NetworkStatisticsMessage import NetworkStatisticsMessage
from ..argument import IArguments
from ..clock import IClock
from ..expire.ExpireReceiveService import ExpireReceiveService
from ..expire.IExpireReceiveListener import IExpireReceiveListener
from ..gpio.IGpioServerService import IGpioServerService
from ..latency.ILatencyServerService import ILatencyServerService
from ..message import message_types
from ..priority.PriorityReceiveService import PriorityReceiveService
from ..receive import IReceiveListener
from ..reliable import IReliableConnectListener, IReliableDisconnectListener, IReliableService
from ..routed.RoutedReceiveService import RoutedReceiveService
from ..service import AbstractServiceManager
from ..throttle.ThrottleServerService import ThrottleServerArguments, ThrottleServerService
from ..timeout.ITimeoutReceiveListener import ITimeoutReceiveListener
from ..timeout.TimeoutReceiveService import TimeoutReceiveService
from ..util.Atomic import Atomic
from ..util.ConnectionDetails import ConnectionDetails
from ..util.Lazy import Lazy


class CarServerArguments(IArguments):
    def __init__(self) -> None:
        self.priority_timeout_seconds = Lazy(lambda store: 1.0)
        self.throttle = ThrottleServerArguments()


class CarServerService(
    IExpireReceiveListener,
    IReceiveListener,
    IReliableConnectListener,
    IReliableDisconnectListener,
    ITimeoutReceiveListener,
):
    def __init__(
            self,
            arguments: CarServerArguments,
            clock: IClock,
            gpio_service: IGpioServerService,
            latency_service: ILatencyServerService,
            reliable_service: IReliableService,
            routed_receive_service: RoutedReceiveService,
            service_manager: AbstractServiceManager,
    ) -> None:
        self.logger = getLogger(__name__)
        self.expire_service = ExpireReceiveService(PriorityReceiveService(
            clock, routed_receive_service.create_receive_service(message_types.car),
            service_manager, arguments.priority_timeout_seconds.get())).add_expire_listener(self)
        self.network_statistics = Atomic(NetworkStatisticsMessage(0, 0, 0))
        self.throttle_service = ThrottleServerService(
            arguments.throttle, gpio_service, latency_service, TimeoutReceiveService(
                clock, self.expire_service, service_manager).add_receive_listener(self).add_timeout_listener(self))
        reliable_service.add_reliable_connect_listener(self).add_reliable_disconnect_listener(self)

    def on_expire_receive(self, message: bytes, details: ConnectionDetails) -> None:
        with self.network_statistics as (network_statistics, _):
            network_statistics.expire_receive_count += 1

    def on_receive(self, message: bytes, details: ConnectionDetails) -> None:
        with self.network_statistics as (network_statistics, _):
            network_statistics.receive_count += 1
        car_message = CarMessage.decode(message)
        self.throttle_service.update(car_message.speed, car_message.steering)

    def on_reliable_connect(self, details: ConnectionDetails) -> None:
        with self.expire_service.last_message_number as (_, set_last_message_number):
            set_last_message_number(0)
        with self.network_statistics as (network_statistics, _):
            network_statistics.expire_receive_count = 0
            network_statistics.receive_count = 0
            network_statistics.timeout_receive_count = 0

    def on_reliable_disconnect(self, details: ConnectionDetails) -> None:
        with self.network_statistics as (network_statistics, _):
            self.logger.info(
                f'Client statistics: receive={network_statistics.receive_count}, '
                f'expire={network_statistics.expire_receive_count}, timeout={network_statistics.timeout_receive_count}')

    def on_timeout_receive(self) -> None:
        with self.network_statistics as (network_statistics, _):
            network_statistics.timeout_receive_count += 1

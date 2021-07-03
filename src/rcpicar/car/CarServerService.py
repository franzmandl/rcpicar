from __future__ import annotations
from logging import getLogger
from .CarMessage import CarMessage
from .NetworkStatisticsMessage import NetworkStatisticsMessage
from ..expire.interfaces import IExpireReceiveListener, IExpireReceiveService
from ..gpio.interfaces import IGpioService
from ..receive import IReceiveListener
from ..reliable import IReliableConnectListener, IReliableDisconnectListener, IReliableService
from ..timeout.interfaces import ITimeoutReceiveListener, ITimeoutReceiveService
from ..util.Atomic import Atomic
from ..util.ConnectionDetails import ConnectionDetails


class CarServerService(
    IExpireReceiveListener,
    IReceiveListener,
    IReliableConnectListener,
    IReliableDisconnectListener,
    ITimeoutReceiveListener,
):
    def __init__(
            self,
            expire_service: IExpireReceiveService,
            gpio_service: IGpioService,
            reliable_service: IReliableService,
            timeout_service: ITimeoutReceiveService,
    ) -> None:
        self.expire_service = expire_service.add_expire_listener(self)
        self.gpio_service = gpio_service
        self.logger = getLogger(__name__)
        self.network_statistics = Atomic(NetworkStatisticsMessage(0, 0, 0))
        reliable_service.add_reliable_connect_listener(self).add_reliable_disconnect_listener(self)
        timeout_service.add_timeout_listener(self).add_receive_listener(self)

    def on_expire_receive(self, message: bytes, details: ConnectionDetails) -> None:
        with self.network_statistics as (network_statistics, _):
            network_statistics.expire_receive_count += 1

    def on_receive(self, message: bytes, details: ConnectionDetails) -> None:
        with self.network_statistics as (network_statistics, _):
            network_statistics.receive_count += 1
        car_message = CarMessage.decode(message)
        self.gpio_service.update(car_message.speed, car_message.steering)

    def on_reliable_connect(self, details: ConnectionDetails) -> None:
        self.expire_service.reset()
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
        self.gpio_service.reset()
        with self.network_statistics as (network_statistics, _):
            network_statistics.timeout_receive_count += 1

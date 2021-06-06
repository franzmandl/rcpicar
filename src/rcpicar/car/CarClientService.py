from __future__ import annotations
from logging import getLogger
from typing import Tuple
from .CarMessage import CarMessage
from ..argument import AnyArguments, IArguments, ValueArgument
from ..clock import IClock
from ..expire.ExpireSendService import ExpireSendService
from ..message import message_types
from ..reliable import IReliableConnectListener, IReliableDisconnectListener, IReliableService
from ..routed.RoutedSendService import RoutedSendService
from ..priority.PrioritySendService import PrioritySendService
from ..service import AbstractServiceManager
from ..timeout.TimeoutSendService import TimeoutSendService
from ..util.Lazy import Lazy
from ..util.ConnectionDetails import ConnectionDetails


class CarClientArguments(IArguments):
    def __init__(self) -> None:
        self.priority = Lazy(lambda store: 128)
        self.send_timeout_seconds = Lazy(lambda store: 0.125)

    def get_arguments(self) -> AnyArguments:
        return [ValueArgument(self.priority, '--priority', int, 'Priority of client.')]


class CarClientService(IReliableConnectListener, IReliableDisconnectListener):
    def __init__(
            self,
            arguments: CarClientArguments,
            clock: IClock,
            reliable_service: IReliableService,
            routed_send_service: RoutedSendService,
            service_manager: AbstractServiceManager,
    ) -> None:
        self._car_message = CarMessage(0, 0)
        self.logger = getLogger(__name__)
        self.timeout_send_service = TimeoutSendService(
            clock,
            arguments.send_timeout_seconds.get(),
            ExpireSendService(
                PrioritySendService(
                    arguments.priority.get(),
                    routed_send_service.create_send_service(message_types.car))),
            service_manager,
        )
        reliable_service.add_reliable_connect_listener(self).add_reliable_disconnect_listener(self)

    def on_reliable_connect(self, details: ConnectionDetails) -> None:
        self.timeout_send_service.set_and_send_immediately(lambda: self._car_message.encode())

    def on_reliable_disconnect(self, details: ConnectionDetails) -> None:
        self.timeout_send_service.set_and_send_immediately(lambda: None)
        with self.timeout_send_service.send_count as (send_count, _):
            self.logger.info(f'Client statistics: sent={send_count}')

    def update(self, speed: int, steering: int) -> Tuple[int, int]:
        self.timeout_send_service.set_and_send_immediately(lambda: self._car_message.update(speed, steering).encode())
        return speed, steering

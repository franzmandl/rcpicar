from __future__ import annotations
from logging import getLogger
from .CarMessage import CarMessage
from ..gpio.interfaces import IGpioService
from ..reliable import IReliableConnectListener, IReliableDisconnectListener, IReliableService
from ..timeout.interfaces import ITimeoutSendService
from ..util.ConnectionDetails import ConnectionDetails


class CarClientService(IGpioService, IReliableConnectListener, IReliableDisconnectListener):
    def __init__(
            self,
            reliable_service: IReliableService,
            timeout_send_service: ITimeoutSendService,
    ) -> None:
        self._car_message = CarMessage(0, 0)
        self.logger = getLogger(__name__)
        self.timeout_send_service = timeout_send_service
        reliable_service.add_reliable_connect_listener(self).add_reliable_disconnect_listener(self)

    def on_reliable_connect(self, details: ConnectionDetails) -> None:
        self.timeout_send_service.set_and_send_immediately(lambda: self._car_message.encode())

    def on_reliable_disconnect(self, details: ConnectionDetails) -> None:
        self.timeout_send_service.set_and_send_immediately(lambda: None)
        self.logger.info(f'Client statistics: sent={self.timeout_send_service.get_send_count()}')

    def update(self, speed: int, steering: int) -> None:
        self.timeout_send_service.set_and_send_immediately(lambda: self._car_message.update(speed, steering).encode())

from logging import getLogger
from threading import Event
from typing import Optional
from ..service import AbstractStartedService, AbstractServiceManager
from ..routed.IRoutedReceiveListener import IRoutedReceiveListener
from ..message import message_types
from ..routed.RoutedReceiveService import RoutedReceiveService
from ..util.ConnectionDetails import ConnectionDetails


class StopServerService(AbstractStartedService, IRoutedReceiveListener):
    def __init__(
            self,
            routed_receive_service: RoutedReceiveService,
            service_manager: AbstractServiceManager
    ) -> None:
        super().__init__(service_manager)
        self.event = Event()
        self.logger = getLogger(__name__)
        routed_receive_service.add_receive_listener(message_types.stop, self)

    def get_service_name(self) -> str:
        return __name__

    def join_service(self, timeout_seconds: Optional[float] = None) -> bool:
        return not self.event.is_set()

    def on_routed_receive(self, message_type: int, message: bytes, details: ConnectionDetails) -> None:
        self.event.set()

    def wait(self) -> None:
        try:
            self.event.wait()
        except KeyboardInterrupt:
            self.logger.info('terminating . . .')

    def stop_service(self) -> None:
        self.event.set()

from logging import getLogger
from threading import Event
from typing import Optional
from .interfaces import IStopServerService
from ..receive import IReceiveListener, IReceiveService
from ..service import IStartedService, IServiceManager
from ..util.ConnectionDetails import ConnectionDetails


class StopServerService(IStartedService, IStopServerService, IReceiveListener):
    def __init__(
            self,
            receive_service: IReceiveService,
            service_manager: IServiceManager
    ) -> None:
        self.event = Event()
        self.logger = getLogger(__name__)
        receive_service.add_receive_listener(self)
        service_manager.add_started_service(self)

    def get_service_name(self) -> str:
        return __name__

    def join_service(self, timeout_seconds: Optional[float] = None) -> bool:
        return not self.event.is_set()

    def on_receive(self, message: bytes, details: ConnectionDetails) -> None:
        self.event.set()

    def wait(self) -> None:
        try:
            self.event.wait()
        except KeyboardInterrupt:
            self.logger.info('terminating . . .')

    def stop_service(self) -> None:
        self.event.set()

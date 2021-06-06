from __future__ import annotations
from logging import getLogger
from .Placeholder import Placeholder
from ..clock import IClock
from ..service import AbstractService, AbstractStartedService, AbstractServiceManager, StartedServiceWrapper


class SingleServiceManager(AbstractServiceManager):
    def __init__(self, clock: IClock) -> None:
        super().__init__(clock)
        self.logger = getLogger(__name__)
        self._not_started_service: Placeholder[AbstractService] = Placeholder()
        self._running_service: Placeholder[AbstractStartedService] = Placeholder()
        self._stopped_service: Placeholder[AbstractStartedService] = Placeholder()

    def add_service(self, service: AbstractService) -> None:
        self._not_started_service.set(service)

    def add_started_service(self, service: AbstractStartedService) -> None:
        self._running_service.set(service)

    def is_service_running(self) -> bool:
        return self._running_service.is_present()

    def join_all(self) -> None:
        service = self._stopped_service.get_optional_and_clear()
        if service is not None:
            service.join_service()

    def start_all(self) -> None:
        service = self._not_started_service.get_and_clear()
        service.start_service()
        StartedServiceWrapper(service, self)

    def stop_all(self) -> None:
        service = self._running_service.get_optional_and_clear()
        if service is not None:
            try:
                service.stop_service()
                self._stopped_service.set(service)
            except BaseException as exception:
                self.logger.exception(f'Stopping service "{type(service)}" threw exception.', exc_info=exception)

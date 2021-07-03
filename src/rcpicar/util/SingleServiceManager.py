from __future__ import annotations
from logging import getLogger
from .Placeholder import Placeholder
from ..service import IService, IStartedService, IServiceManager, StartedServiceWrapper


class SingleServiceManager(IServiceManager):
    def __init__(self) -> None:
        self.logger = getLogger(__name__)
        self._not_started_service: Placeholder[IService] = Placeholder()
        self._running_service: Placeholder[IStartedService] = Placeholder()
        self._stopped_service: Placeholder[IStartedService] = Placeholder()

    def add_service(self, service: IService) -> None:
        self._not_started_service.set(service)

    def add_started_service(self, service: IStartedService) -> None:
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

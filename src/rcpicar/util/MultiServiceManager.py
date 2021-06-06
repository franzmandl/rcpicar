from __future__ import annotations
from logging import getLogger
from typing import List
from .FirstInLastOut import FirstInLastOut
from ..clock import IClock
from ..service import AbstractService, AbstractStartedService, AbstractServiceManager, StartedServiceWrapper


class MultiServiceManager(AbstractServiceManager):
    def __init__(self, clock: IClock, join_timeout_seconds: float = 0.1) -> None:
        super().__init__(clock)
        self._join_timeout_seconds = join_timeout_seconds
        self._logger = getLogger(__name__)
        self._not_started_services: FirstInLastOut[AbstractService] = FirstInLastOut()
        self._running_services: FirstInLastOut[AbstractStartedService] = FirstInLastOut()
        self._stopped_services: FirstInLastOut[AbstractStartedService] = FirstInLastOut()

    def add_service(self, service: AbstractService) -> None:
        self._not_started_services.append(service)

    def add_started_service(self, service: AbstractStartedService) -> None:
        self._running_services.append(service)

    def join_all(self) -> None:
        stubborn_services: List[AbstractStartedService] = []
        while True:
            service = self._stopped_services.pop()
            if service is None:
                break
            if service.join_service(self._join_timeout_seconds):
                stubborn_services.append(service)
        for service in stubborn_services:
            self._logger.info(f'Waiting for stubborn service "{service.get_service_name()}".')
            service.join_service()

    def start_all(self) -> None:
        while True:
            service = self._not_started_services.pop()
            if service is None:
                break
            service.start_service()
            StartedServiceWrapper(service, self)

    def stop_all(self) -> None:
        while True:
            service = self._running_services.pop()
            if service is None:
                break
            try:
                service.stop_service()
                self._stopped_services.append(service)
            except BaseException as exception:
                self._logger.exception(
                    f'Stopping service "{service.get_service_name()}" threw exception.', exc_info=exception)

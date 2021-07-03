from __future__ import annotations
from logging import getLogger
from typing import List
from .FirstInLastOut import FirstInLastOut
from ..service import IService, IStartedService, IServiceManager, StartedServiceWrapper


class MultiServiceManager(IServiceManager):
    def __init__(self, join_timeout_seconds: float = 0.1) -> None:
        self._join_timeout_seconds = join_timeout_seconds
        self._logger = getLogger(__name__)
        self._not_started_services: FirstInLastOut[IService] = FirstInLastOut()
        self._running_services: FirstInLastOut[IStartedService] = FirstInLastOut()
        self._stopped_services: FirstInLastOut[IStartedService] = FirstInLastOut()

    def add_service(self, service: IService) -> None:
        self._not_started_services.append(service)

    def add_started_service(self, service: IStartedService) -> None:
        self._running_services.append(service)

    def join_all(self) -> None:
        stubborn_services: List[IStartedService] = []
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

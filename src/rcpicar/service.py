from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional


class IService(ABC):
    @abstractmethod
    def get_service_name(self) -> str:
        """"""

    @abstractmethod
    def join_service(self, timeout_seconds: Optional[float] = None) -> bool:
        """
        :return: True if services is still running, False otherwise.
        """

    @abstractmethod
    def start_service(self) -> None:
        """"""

    @abstractmethod
    def stop_service(self) -> None:
        """"""


class IStartedService(ABC):
    @abstractmethod
    def get_service_name(self) -> str:
        """"""

    @abstractmethod
    def join_service(self, timeout_seconds: Optional[float] = None) -> bool:
        """"""

    @abstractmethod
    def stop_service(self) -> None:
        """"""


class StartedServiceWrapper(IStartedService):
    def __init__(self, service: IService, service_manager: IServiceManager) -> None:
        self.service = service
        service_manager.add_started_service(self)

    def get_service_name(self) -> str:
        return self.service.get_service_name()

    def join_service(self, timeout_seconds: Optional[float] = None) -> bool:
        return self.service.join_service(timeout_seconds)

    def stop_service(self) -> None:
        self.service.stop_service()


class IServiceManager(ABC):
    @abstractmethod
    def add_service(self, service: IService) -> None:
        """"""

    @abstractmethod
    def add_started_service(self, service: IStartedService) -> None:
        """"""

    @abstractmethod
    def join_all(self) -> None:
        """"""

    @abstractmethod
    def start_all(self) -> None:
        """"""

    @abstractmethod
    def stop_all(self) -> None:
        """"""

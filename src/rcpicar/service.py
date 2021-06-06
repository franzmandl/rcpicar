from __future__ import annotations
from abc import ABC, abstractmethod
from types import TracebackType
from typing import Optional, Type
from .clock import IClock


class AbstractService(ABC):
    def __init__(self, service_manager: AbstractServiceManager) -> None:
        service_manager.add_service(self)

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


class AbstractStartedService(ABC):
    def __init__(self, service_manager: AbstractServiceManager) -> None:
        service_manager.add_started_service(self)

    @abstractmethod
    def get_service_name(self) -> str:
        """"""

    @abstractmethod
    def join_service(self, timeout_seconds: Optional[float] = None) -> bool:
        """"""

    @abstractmethod
    def stop_service(self) -> None:
        """"""


class StartedServiceWrapper(AbstractStartedService):
    def __init__(self, service: AbstractService, service_manager: AbstractServiceManager) -> None:
        super().__init__(service_manager)
        self.service = service

    def get_service_name(self) -> str:
        return self.service.get_service_name()

    def join_service(self, timeout_seconds: Optional[float] = None) -> bool:
        return self.service.join_service(timeout_seconds)

    def stop_service(self) -> None:
        self.service.stop_service()


class AbstractServiceManager(ABC):
    def __init__(self, clock: IClock) -> None:
        self.clock = clock

    @abstractmethod
    def add_service(self, service: AbstractService) -> None:
        """"""

    @abstractmethod
    def add_started_service(self, service: AbstractStartedService) -> None:
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

    def __enter__(self) -> None:
        self.start_all()

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType]
    ) -> None:
        self.stop_all()
        self.clock.notify()
        self.join_all()

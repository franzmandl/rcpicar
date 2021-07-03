from abc import ABC, abstractmethod
from typing import Tuple
from ..util.Placeholder import Placeholder


class IDiscoveryClientService(ABC):
    @abstractmethod
    def get_server_address(self) -> Placeholder[Tuple[str, int]]:
        """"""

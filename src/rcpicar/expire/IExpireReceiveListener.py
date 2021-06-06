from abc import ABC, abstractmethod
from ..util.ConnectionDetails import ConnectionDetails


class IExpireReceiveListener(ABC):
    @abstractmethod
    def on_expire_receive(self, message: bytes, details: ConnectionDetails) -> None:
        """"""

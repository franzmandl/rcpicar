from abc import ABC, abstractmethod
from typing import Union


class _MessageTypes:
    def __init__(self) -> None:
        message_type_generator = iter(range(2**8))
        self.car = next(message_type_generator)
        self.custom = next(message_type_generator)
        self.gstreamer = next(message_type_generator)
        self.latency = next(message_type_generator)
        self.stop = next(message_type_generator)


message_types = _MessageTypes()


class IMessage(ABC):
    @abstractmethod
    def encode(self) -> bytes:
        """"""


Payload = Union[bytes, IMessage]


def encode_payload(payload: Payload) -> bytes:
    return payload.encode() if isinstance(payload, IMessage) else payload

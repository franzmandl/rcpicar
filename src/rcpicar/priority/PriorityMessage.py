from __future__ import annotations
from struct import pack, unpack
from typing import cast, Tuple
from ..message import encode_payload, IMessage, Payload
from ..util.struct import get_required_size

format_string = '<B'
format_length = get_required_size(format_string)
format_type = Tuple[int]


class PriorityMessage(IMessage):
    def __init__(self, priority: int, payload: Payload) -> None:
        self.priority = priority
        self.payload = encode_payload(payload)

    def encode(self) -> bytes:
        return pack(format_string, self.priority) + self.payload

    @staticmethod
    def decode(message: bytes) -> PriorityMessage:
        priority, = cast(format_type, unpack(format_string, message[:format_length]))
        return PriorityMessage(priority, message[format_length:])

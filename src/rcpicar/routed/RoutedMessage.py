from __future__ import annotations
from struct import pack, unpack
from typing import cast, Tuple
from ..message import encode_payload, IMessage, Payload
from ..util.struct import get_required_size

format_string = '<B'
format_length = get_required_size(format_string)
format_type = Tuple[int]


class RoutedMessage(IMessage):
    def __init__(self, message_type: int, payload: Payload) -> None:
        self.message_type = message_type
        self.payload = encode_payload(payload)

    def encode(self) -> bytes:
        return pack(format_string, self.message_type) + self.payload

    @staticmethod
    def decode(message: bytes) -> RoutedMessage:
        message_type, = cast(format_type, unpack(format_string, message[:format_length]))
        return RoutedMessage(message_type, message[format_length:])

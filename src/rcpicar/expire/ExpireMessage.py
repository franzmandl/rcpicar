from __future__ import annotations
from struct import pack, unpack
from typing import cast, Tuple
from ..message import encode_payload, IMessage, Payload
from ..util.struct import get_required_size

format_string = '<H'
format_length = get_required_size(format_string)
format_type = Tuple[int]
message_number_range = 2**16
highest_message_number = message_number_range - 1
valid_message_number_range = message_number_range >> 2  # == message_number_range / 4


class ExpireMessage(IMessage):
    def __init__(self, message_number: int, payload: Payload) -> None:
        self.message_number = message_number
        self.payload = encode_payload(payload)

    def encode(self) -> bytes:
        return pack(format_string, self.message_number) + self.payload

    @staticmethod
    def decode(message: bytes) -> ExpireMessage:
        message_number, = cast(format_type, unpack(format_string, message[:format_length]))
        return ExpireMessage(message_number, message[format_length:])

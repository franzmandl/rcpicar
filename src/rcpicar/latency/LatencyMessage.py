from __future__ import annotations
from struct import pack, unpack
from typing import cast, Tuple
from ..message import IMessage

format_string = '<B'
format_type = Tuple[int]
max_number = 2**8


class LatencyMessage(IMessage):
    def __init__(self, number: int) -> None:
        self.number = number

    def encode(self) -> bytes:
        return pack(format_string, self.number)

    def increment(self) -> None:
        self.number = (self.number + 1) % max_number

    @staticmethod
    def decode(message: bytes) -> LatencyMessage:
        number, = cast(format_type, unpack(format_string, message))
        return LatencyMessage(number)

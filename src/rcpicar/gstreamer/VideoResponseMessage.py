from __future__ import annotations
from struct import pack, unpack
from typing import cast, Tuple
from ..message import IMessage
from ..util.struct import get_required_size

format_string = '<H'
format_length = get_required_size(format_string)
format_type = Tuple[int]


class VideoResponseMessage(IMessage):
    def __init__(self, caps: str, port: int) -> None:
        self.caps = caps
        self.port = port

    def encode(self) -> bytes:
        return pack(format_string, self.port) + self.caps.encode()

    @staticmethod
    def decode(message: bytes) -> VideoResponseMessage:
        port, = cast(format_type, unpack(format_string, message[:format_length]))
        caps = message[format_length:].decode()
        return VideoResponseMessage(caps, port)

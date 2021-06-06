from __future__ import annotations
from struct import pack, unpack
from typing import cast, Tuple
from ..message import IMessage
from ..constants import discovery_magic_response_bytes

format_string = '<H'
format_type = Tuple[int]


class DiscoveryResponseMessage(IMessage):
    def __init__(self, port: int) -> None:
        self.port = port

    def encode(self) -> bytes:
        return discovery_magic_response_bytes + pack(format_string, self.port)

    @staticmethod
    def decode(message: bytes) -> DiscoveryResponseMessage:
        magic_bytes_length = len(discovery_magic_response_bytes)
        port, = cast(format_type, unpack(format_string, message[magic_bytes_length:]))
        return DiscoveryResponseMessage(port)

    @staticmethod
    def is_valid(message: bytes) -> bool:
        return message.startswith(discovery_magic_response_bytes)

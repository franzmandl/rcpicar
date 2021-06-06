from __future__ import annotations
from ..constants import discovery_magic_request_bytes


class DiscoveryRequestMessage:
    @staticmethod
    def encode() -> bytes:
        return discovery_magic_request_bytes

    @staticmethod
    def is_valid(message: bytes) -> bool:
        return message == discovery_magic_request_bytes

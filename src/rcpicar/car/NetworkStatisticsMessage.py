from __future__ import annotations
from ..message import IMessage

separator = ','


class NetworkStatisticsMessage(IMessage):
    def __init__(self, expire_receive_count: int, receive_count: int, timeout_receive_count: int) -> None:
        self.expire_receive_count = expire_receive_count
        self.receive_count = receive_count
        self.timeout_receive_count = timeout_receive_count

    def encode(self) -> bytes:
        return separator.join([
            str(self.expire_receive_count),
            str(self.receive_count),
            str(self.timeout_receive_count),
        ]).encode()

    @staticmethod
    def decode(message: bytes) -> NetworkStatisticsMessage:
        expire_receive_count, receive_count, timeout_receive_count = message.decode().split(separator)
        return NetworkStatisticsMessage(int(expire_receive_count), int(receive_count), int(timeout_receive_count))

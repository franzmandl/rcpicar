from __future__ import annotations
from typing import Tuple
from .VideoSettings import VideoSettings
from ..message import IMessage

separator = ','


class GStreamerRequestMessage(IMessage):
    def __init__(self, address: Tuple[str, int], settings: VideoSettings) -> None:
        self.address = address
        self.settings = settings

    def encode(self) -> bytes:
        return separator.join([
            self.address[0],
            str(self.address[1]),
            str(self.settings.bit_rate),
            str(self.settings.fps),
            str(self.settings.height),
            str(self.settings.width)
        ]).encode()

    @staticmethod
    def decode(message: bytes) -> GStreamerRequestMessage:
        ip, port, bit_rate, fps, height, width = message.decode().split(separator)
        return GStreamerRequestMessage((ip, int(port)), VideoSettings(int(bit_rate), int(fps), int(height), int(width)))

from __future__ import annotations
from abc import ABC, abstractmethod


class IGStreamerVideoListener(ABC):
    @abstractmethod
    def on_video_available(self, caps: str, port: int) -> None:
        """"""


class IGStreamerClientService(ABC):
    @abstractmethod
    def add_gstreamer_video_listener(self, listener: IGStreamerVideoListener) -> IGStreamerClientService:
        """"""

    @abstractmethod
    def open_video(self, ip: str) -> None:
        """"""

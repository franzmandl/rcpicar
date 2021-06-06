from abc import ABC, abstractmethod


class GStreamerVideoListener(ABC):
    @abstractmethod
    def on_video_available(self, caps: str, port: int) -> None:
        """"""

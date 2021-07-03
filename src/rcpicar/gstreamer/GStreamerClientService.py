from __future__ import annotations
from .interfaces import IGStreamerClientService, IGStreamerVideoListener
from .GStreamerRequestMessage import GStreamerRequestMessage
from .GStreamerResponseMessage import GstreamerResponseMessage
from .VideoSettings import VideoSettings
from ..constants import default_gstreamer_port
from ..receive import IReceiveListener, IReceiveService
from ..send import ISendService
from ..util.argument import AnyArguments, create_value_argument, IArguments
from ..util.ConnectionDetails import ConnectionDetails
from ..util.Lazy import Lazy
from ..util.Listeners import Listeners


class GStreamerClientArguments(IArguments):
    def __init__(self) -> None:
        self.bit_rate = Lazy(lambda store: 2000000)
        self.fps = Lazy(lambda store: 30)
        self.height = Lazy(lambda store: 720)
        self.port = Lazy(lambda store: default_gstreamer_port)
        self.width = Lazy(lambda store: 1280)
        self.settings = Lazy(lambda store: VideoSettings(
            self.bit_rate(store),
            self.fps(store),
            self.height(store),
            self.width(store),
        ))

    def get_arguments(self) -> AnyArguments:
        return [
            create_value_argument(self.bit_rate, '--video-bit-rate', int, 'Video quality parameter.'),
            create_value_argument(self.fps, '--video-fps', int, 'Video frames per second.'),
            create_value_argument(self.height, '--video-height', int, 'Video resolution height.'),
            create_value_argument(self.port, '--video-port', int, 'Video stream port.'),
            create_value_argument(self.width, '--video-width', int, 'Video resolution width.'),
        ]


class GStreamerClientService(IGStreamerClientService, IReceiveListener):
    def __init__(
            self,
            arguments: GStreamerClientArguments,
            receive_service: IReceiveService,
            send_service: ISendService,
    ) -> None:
        self.arguments = arguments
        self.send_service = send_service
        self.listeners: Listeners[IGStreamerVideoListener] = Listeners()
        receive_service.add_receive_listener(self)

    def add_gstreamer_video_listener(self, listener: IGStreamerVideoListener) -> GStreamerClientService:
        self.listeners.add_listener(listener)
        return self

    def open_video(self, ip: str) -> None:
        self.send_service.send(GStreamerRequestMessage(
            (ip, self.arguments.port.get()), self.arguments.settings.get()
        ).encode())

    def on_receive(self, message: bytes, details: ConnectionDetails) -> None:
        response = GstreamerResponseMessage.decode(message)
        self.listeners.for_each(lambda listener: listener.on_video_available(response.caps, response.port))

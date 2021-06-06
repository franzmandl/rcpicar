from __future__ import annotations
from .GStreamerVideoListener import GStreamerVideoListener
from .VideoRequestMessage import VideoRequestMessage
from .VideoResponseMessage import VideoResponseMessage
from .VideoSettings import VideoSettings
from ..argument import AnyArguments, IArguments, ValueArgument
from ..constants import default_video_port
from ..message import message_types
from ..routed.IRoutedReceiveListener import IRoutedReceiveListener
from ..routed.RoutedReceiveService import RoutedReceiveService
from ..routed.RoutedSendService import RoutedSendService
from ..util.ConnectionDetails import ConnectionDetails
from ..util.Lazy import Lazy
from ..util.Listeners import Listeners


class GStreamerClientArguments(IArguments):
    def __init__(self) -> None:
        self.flv_file_path = Lazy(lambda store: None)
        self.bit_rate = Lazy(lambda store: 2000000)
        self.fps = Lazy(lambda store: 30)
        self.height = Lazy(lambda store: 720)
        self.port = Lazy(lambda store: default_video_port)
        self.width = Lazy(lambda store: 1280)
        self.settings = Lazy(lambda store: VideoSettings(
            self.bit_rate(store),
            self.fps(store),
            self.height(store),
            self.width(store),
        ))

    def get_arguments(self) -> AnyArguments:
        return [
            ValueArgument(self.flv_file_path, '--flv-file-path', str, 'Store video stream additionally to this file.'),
            ValueArgument(self.bit_rate, '--video-bit-rate', int, 'Video quality parameter.'),
            ValueArgument(self.fps, '--video-fps', int, 'Video frames per second.'),
            ValueArgument(self.height, '--video-height', int, 'Video resolution height.'),
            ValueArgument(self.port, '--video-port', int, 'Video stream port.'),
            ValueArgument(self.width, '--video-width', int, 'Video resolution width.'),
        ]


class GStreamerClientService(IRoutedReceiveListener):
    def __init__(
            self,
            arguments: GStreamerClientArguments,
            routed_receive_service: RoutedReceiveService,
            routed_send_service: RoutedSendService,
    ) -> None:
        self.arguments = arguments
        self.routed_send_service = routed_send_service
        self.listeners: Listeners[GStreamerVideoListener] = Listeners()
        routed_receive_service.add_receive_listener(message_types.video, self)

    def add_gstreamer_video_listener(self, listener: GStreamerVideoListener) -> GStreamerClientService:
        self.listeners.add_listener(listener)
        return self

    def open_video(self, ip: str) -> None:
        self.routed_send_service.send(message_types.video, VideoRequestMessage(
            (ip, self.arguments.port.get()), self.arguments.settings.get()
        ).encode())

    def on_routed_receive(self, message_type: int, message: bytes, details: ConnectionDetails) -> None:
        response = VideoResponseMessage.decode(message)
        self.listeners.for_each(lambda listener: listener.on_video_available(response.caps, response.port))

from typing import Generic, Tuple, TypeVar
from rcpicar.car.CarMessage import CarMessage
from rcpicar.expire.ExpireMessage import ExpireMessage
from rcpicar.gstreamer.VideoRequestMessage import VideoRequestMessage
from rcpicar.gstreamer.VideoResponseMessage import VideoResponseMessage
from rcpicar.gstreamer.VideoSettings import VideoSettings
from rcpicar.latency.LatencyMessage import LatencyMessage
from rcpicar.message import message_types, IMessage
from rcpicar.priority.PriorityMessage import PriorityMessage
from rcpicar.routed.RoutedMessage import RoutedMessage
from rcpicar.util.ConnectionDetails import ConnectionDetails

messages = [
    b'jsehnv98e4fi',
    b'8923jd539845j',
    b'fjs9e4osf65',
    b'k8z7694rfgu',
    b'snd485r49756g',
    b'kds54hf76',
]
mock_client_address = ('client', 1257)
mock_server_address = ('server', 5682)
mock_reconnect_seconds = 10.0
mock_details = ConnectionDetails(mock_client_address, mock_server_address)
mock_video_settings = VideoSettings(8, 4, 9, 7)

MT = TypeVar('MT', bound=IMessage)


class RoutedMessageWrapper:
    def __init__(self, message: RoutedMessage) -> None:
        self.message = message

    def encode(self) -> bytes:
        return self.message.encode()

    def udp_tuple(self, is_server: bool) -> Tuple[bytes, Tuple[str, int]]:
        return self.message.encode(), mock_server_address if is_server else mock_client_address


class TypedMessageWrapper(Generic[MT]):
    def __init__(self, message: MT, message_type: int) -> None:
        self.message = message
        self.message_type = message_type

    def routed(self) -> RoutedMessageWrapper:
        return RoutedMessageWrapper(RoutedMessage(self.message_type, self.message))


class ExpireMessageWrapper:
    def __init__(self, message: ExpireMessage, message_type: int) -> None:
        self.message = message
        self.message_type = message_type

    def priority(self, priority: int) -> TypedMessageWrapper[PriorityMessage]:
        return TypedMessageWrapper(PriorityMessage(priority, self.message), self.message_type)


class CarMessageWrapper:
    def __init__(self, message: CarMessage, message_type: int) -> None:
        self.message = message
        self.message_type = message_type

    def expire(self, message_number: int) -> ExpireMessageWrapper:
        return ExpireMessageWrapper(ExpireMessage(message_number, self.message), self.message_type)


def create_car_message(speed: int, steering: int) -> CarMessageWrapper:
    return CarMessageWrapper(CarMessage(speed, steering), message_types.car)


def create_latency_message(number: int) -> TypedMessageWrapper[LatencyMessage]:
    return TypedMessageWrapper(LatencyMessage(number), message_types.latency)


def create_video_request_message(
        address: Tuple[str, int], settings: VideoSettings
) -> TypedMessageWrapper[VideoRequestMessage]:
    return TypedMessageWrapper(VideoRequestMessage(address, settings), message_types.video)


def create_video_response_message(caps: str, port: int) -> TypedMessageWrapper[VideoResponseMessage]:
    return TypedMessageWrapper(VideoResponseMessage(caps, port), message_types.video)

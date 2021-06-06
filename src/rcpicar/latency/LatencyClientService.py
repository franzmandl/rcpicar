from ..message import message_types
from ..receive import IReceiveListener
from ..routed.RoutedReceiveService import RoutedReceiveService
from ..routed.RoutedSendService import RoutedSendService
from ..util.ConnectionDetails import ConnectionDetails


class LatencyClientService(IReceiveListener):
    def __init__(
            self,
            routed_receive_service: RoutedReceiveService,
            routed_send_service: RoutedSendService,
    ) -> None:
        self.send_service = routed_send_service.create_send_service(message_types.latency)
        routed_receive_service.create_receive_service(message_types.latency).add_receive_listener(self)

    def on_receive(self, message: bytes, details: ConnectionDetails) -> None:
        self.send_service.send(message)

from ..receive import IReceiveListener, IReceiveService
from ..send import ISendService
from ..util.ConnectionDetails import ConnectionDetails


class LatencyClientService(IReceiveListener):
    def __init__(
            self,
            receive_service: IReceiveService,
            send_service: ISendService,
    ) -> None:
        self.send_service = send_service
        receive_service.add_receive_listener(self)

    def on_receive(self, message: bytes, details: ConnectionDetails) -> None:
        self.send_service.send(message)

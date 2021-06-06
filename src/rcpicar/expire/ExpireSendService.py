from .ExpireMessage import ExpireMessage, highest_message_number
from ..send import ISendService
from ..util.Atomic import Atomic


class ExpireSendService(ISendService):
    def __init__(self, send_service: ISendService) -> None:
        self.send_service = send_service
        self.last_message_number = Atomic(1)

    def send(self, message: bytes) -> None:
        with self.last_message_number as (last_message_number, set_last_message_number):
            message_number = last_message_number
            set_last_message_number((last_message_number + 1) % highest_message_number)
        self.send_service.send(ExpireMessage(message_number, message).encode())

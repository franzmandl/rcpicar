from .PriorityMessage import PriorityMessage
from ..send import ISendService


class PrioritySendService(ISendService):
    def __init__(self, priority: int, send_service: ISendService) -> None:
        self.send_service = send_service
        self.priority = priority

    def send(self, message: bytes) -> None:
        self.send_service.send(PriorityMessage(self.priority, message).encode())

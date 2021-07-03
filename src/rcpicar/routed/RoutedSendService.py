from __future__ import annotations
from .interfaces import IRoutedSendService
from .RoutedMessage import RoutedMessage
from ..send import ISendService


class SendService(ISendService):
    def __init__(self, message_type: int, routed_send_service: RoutedSendService) -> None:
        self.message_type = message_type
        self.routed_send_service = routed_send_service

    def send(self, message: bytes) -> None:
        self.routed_send_service.send(self.message_type, message)


class RoutedSendService(IRoutedSendService):
    def __init__(self, send_service: ISendService) -> None:
        self.send_service = send_service

    def create_send_service(self, message_type: int) -> ISendService:
        return SendService(message_type, self)

    def send(self, message_type: int, message: bytes) -> None:
        self.send_service.send(RoutedMessage(message_type, message).encode())

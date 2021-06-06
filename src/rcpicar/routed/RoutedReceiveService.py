from __future__ import annotations
from typing import Dict
from .IRoutedReceiveListener import IRoutedReceiveListener
from .RoutedMessage import RoutedMessage
from ..receive import IReceiveListener, IReceiveService
from ..util.ConnectionDetails import ConnectionDetails
from ..util.Listeners import Listeners


class ReceiveListener(IRoutedReceiveListener):
    def __init__(self, listener: IReceiveListener) -> None:
        self.listener = listener

    def on_routed_receive(self, message_type: int, message: bytes, details: ConnectionDetails) -> None:
        self.listener.on_receive(message, details)


class ReceiveService(IReceiveService):
    def __init__(self, message_type: int, routed_receive_service: RoutedReceiveService) -> None:
        self.message_type = message_type
        self.routed_receive_service = routed_receive_service

    def add_receive_listener(self, listener: IReceiveListener) -> ReceiveService:
        self.routed_receive_service.add_receive_listener(self.message_type, ReceiveListener(listener))
        return self


class RoutedReceiveService(IReceiveListener):
    def __init__(self, receive_service: IReceiveService) -> None:
        self.received_listeners: Dict[int, Listeners[IRoutedReceiveListener]] = dict()
        receive_service.add_receive_listener(self)

    def add_receive_listener(self, message_type: int, listener: IRoutedReceiveListener) -> RoutedReceiveService:
        if message_type > 255:
            raise RuntimeError(f'Illegal message type: {message_type} > 255.')
        if message_type not in self.received_listeners:
            self.received_listeners[message_type] = Listeners()
        self.received_listeners[message_type].add_listener(listener)
        return self

    def create_receive_service(self, message_type: int) -> IReceiveService:
        return ReceiveService(message_type, self)

    def on_receive(self, message: bytes, details: ConnectionDetails) -> None:
        routed_message = RoutedMessage.decode(message)
        self.received_listeners[routed_message.message_type].for_each(
            lambda listener: listener.on_routed_receive(routed_message.message_type, routed_message.payload, details))

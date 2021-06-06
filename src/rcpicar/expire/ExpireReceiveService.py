from __future__ import annotations
from .ExpireMessage import ExpireMessage, highest_message_number, message_number_range, valid_message_number_range
from .IExpireReceiveListener import IExpireReceiveListener
from ..receive import IReceiveListener, IReceiveService
from ..util.Atomic import Atomic
from ..util.ConnectionDetails import ConnectionDetails
from ..util.Listeners import Listeners


class ExpireReceiveService(IReceiveListener, IReceiveService):
    def __init__(self, receive_service: IReceiveService) -> None:
        self.last_message_number = Atomic(0)
        self.expire_listeners: Listeners[IExpireReceiveListener] = Listeners()
        self.receive_listeners: Listeners[IReceiveListener] = Listeners()
        receive_service.add_receive_listener(self)

    def on_receive(self, message: bytes, details: ConnectionDetails) -> None:
        expire_message = ExpireMessage.decode(message)
        with self.last_message_number as (last_message_number, set_last_message_number):
            end_of_valid_range = (last_message_number + valid_message_number_range) % message_number_range
            if expire_message.message_number == highest_message_number:
                is_valid = True
            elif end_of_valid_range < last_message_number:
                is_valid = not end_of_valid_range <= expire_message.message_number <= last_message_number
            else:
                is_valid = last_message_number < expire_message.message_number < end_of_valid_range
            if is_valid:
                set_last_message_number(expire_message.message_number)
        if is_valid:
            self.receive_listeners.for_each(lambda listener: listener.on_receive(expire_message.payload, details))
        else:
            self.expire_listeners.for_each(lambda listener: listener.on_expire_receive(expire_message.payload, details))

    def add_receive_listener(self, listener: IReceiveListener) -> ExpireReceiveService:
        self.receive_listeners.add_listener(listener)
        return self

    def add_expire_listener(self, listener: IExpireReceiveListener) -> ExpireReceiveService:
        self.expire_listeners.add_listener(listener)
        return self

from __future__ import annotations
from queue import Empty
from threading import Thread
from typing import Optional
from .ILatencyListener import ILatencyListener
from .ILatencyServerService import ILatencyServerService
from .LatencyMessage import LatencyMessage
from ..argument import IArguments
from ..clock import IClock
from ..message import message_types
from ..queue_ import IQueue
from ..receive import IReceiveListener
from ..routed.RoutedReceiveService import RoutedReceiveService
from ..routed.RoutedSendService import RoutedSendService
from ..service import AbstractService, AbstractServiceManager
from ..util.ConnectionDetails import ConnectionDetails
from ..util.InterruptableSleep import InterruptableSleep
from ..util.Lazy import Lazy
from ..util.IdealQueue import IdealQueue
from ..util.Listeners import Listeners


class LatencyServerArguments(IArguments):
    def __init__(self) -> None:
        self.latency_check_interval_seconds = Lazy(lambda store: 1.0)


class LatencyServerService(ILatencyServerService, IReceiveListener, AbstractService):
    def __init__(
            self,
            arguments: LatencyServerArguments,
            clock: IClock,
            routed_receive_service: RoutedReceiveService,
            routed_send_service: RoutedSendService,
            service_manager: AbstractServiceManager,
    ) -> None:
        super().__init__(service_manager)
        self.arguments = arguments
        self.clock = clock
        self.interruptable_sleep = InterruptableSleep(clock)
        self.listeners: Listeners[ILatencyListener] = Listeners()
        self.received_messages: IQueue[Optional[LatencyMessage]] = IdealQueue()
        self.send_service = routed_send_service.create_send_service(message_types.latency)
        self.thread = Thread(target=self.run)
        routed_receive_service.create_receive_service(message_types.latency).add_receive_listener(self)

    def get_service_name(self) -> str:
        return __name__

    def join_service(self, timeout_seconds: Optional[float] = None) -> bool:
        self.thread.join(timeout_seconds)
        return self.thread.is_alive()

    def on_receive(self, message: bytes, details: ConnectionDetails) -> None:
        self.received_messages.put(LatencyMessage.decode(message))

    def run(self) -> None:
        sent_message = LatencyMessage(0)
        while True:
            try:
                sent_message.increment()
                sent_timestamp = self.clock.get_seconds()
                self.send_service.send(sent_message.encode())
                while True:
                    timeout_seconds = sent_timestamp + self.arguments.latency_check_interval_seconds.get(
                    ) - self.clock.get_seconds()
                    if timeout_seconds <= 0:
                        raise Empty()
                    received_message = self.clock.get_from_queue(self.received_messages, timeout_seconds)
                    received_timestamp = self.clock.get_seconds()
                    if received_message is None:
                        return
                    if received_message.number == sent_message.number:
                        break
                self.listeners.for_each(lambda listener: listener.on_latency_available(
                    received_timestamp - sent_timestamp))
                if not self.interruptable_sleep.sleep(self.arguments.latency_check_interval_seconds.get()):
                    return
            except Empty:
                self.listeners.for_each(lambda listener: listener.on_latency_timeout())

    def start_service(self) -> None:
        self.thread.start()

    def stop_service(self) -> None:
        self.interruptable_sleep.interrupt()
        self.received_messages.put(None)

    def add_latency_listener(self, latency_listener: ILatencyListener) -> LatencyServerService:
        self.listeners.add_listener(latency_listener)
        return self

from __future__ import annotations
from queue import Empty
from threading import Thread
from typing import Optional, Union
from .interfaces import ITimeoutReceiveListener, ITimeoutReceiveService
from ..clock import IClock
from ..queue_ import IQueue
from ..receive import IReceiveListener, IReceiveService
from ..service import IService, IServiceManager
from ..util.ConnectionDetails import ConnectionDetails
from ..util.IdealQueue import IdealQueue
from ..util.Listeners import Listeners


class ReceiveEvent:
    pass


class SetTimeoutEvent:
    def __init__(self, timeout_seconds: Optional[float]) -> None:
        self.timeout_seconds = timeout_seconds


class StopEvent:
    pass


class TimeoutReceiveService(IService, IReceiveListener, ITimeoutReceiveService):
    def __init__(
            self,
            clock: IClock,
            receive_service: IReceiveService,
            service_manager: IServiceManager,
            timeout_seconds: Optional[float] = None,
    ) -> None:
        self.clock = clock
        self.event_bus: IQueue[Union[ReceiveEvent, SetTimeoutEvent, StopEvent]] = IdealQueue()
        self.receive_listeners: Listeners[IReceiveListener] = Listeners()
        self.thread = Thread(target=self.run)
        self.timeout_listeners: Listeners[ITimeoutReceiveListener] = Listeners()
        self.timeout_seconds = timeout_seconds
        receive_service.add_receive_listener(self)
        service_manager.add_service(self)

    def add_receive_listener(self, listener: IReceiveListener) -> TimeoutReceiveService:
        self.receive_listeners.add_listener(listener)
        return self

    def add_timeout_listener(self, timeout_listener: ITimeoutReceiveListener) -> TimeoutReceiveService:
        self.timeout_listeners.add_listener(timeout_listener)
        return self

    def get_service_name(self) -> str:
        return __name__

    def join_service(self, timeout_seconds: Optional[float] = None) -> bool:
        self.thread.join(timeout_seconds)
        return self.thread.is_alive()

    def on_receive(self, message: bytes, details: ConnectionDetails) -> None:
        self.event_bus.put(ReceiveEvent())
        self.receive_listeners.for_each(lambda listener: listener.on_receive(message, details))

    def run(self) -> None:
        while True:
            try:
                waiting_since_seconds = self.clock.get_seconds()
                while True:
                    if self.timeout_seconds is None:
                        event = self.event_bus.get()
                    else:
                        remaining_seconds = waiting_since_seconds + self.timeout_seconds - self.clock.get_seconds()
                        if remaining_seconds <= 0:
                            raise Empty()
                        event = self.clock.get_from_queue(self.event_bus, remaining_seconds)
                    if isinstance(event, ReceiveEvent):
                        break
                    elif isinstance(event, SetTimeoutEvent):
                        self.timeout_seconds = event.timeout_seconds
                    elif isinstance(event, StopEvent):
                        return
            except Empty:
                self.timeout_listeners.for_each(lambda listener: listener.on_timeout_receive())

    def set_timeout(self, timeout_seconds: float) -> None:
        self.event_bus.put(SetTimeoutEvent(timeout_seconds))

    def start_service(self) -> None:
        self.thread.start()

    def stop_service(self) -> None:
        self.event_bus.put(StopEvent())

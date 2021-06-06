from __future__ import annotations
from threading import Thread
from typing import Optional
from .PriorityMessage import PriorityMessage
from ..clock import IClock
from ..service import AbstractService, AbstractServiceManager
from ..receive import IReceiveListener, IReceiveService
from ..util.Atomic import Atomic
from ..util.ConnectionDetails import ConnectionDetails
from ..util.InterruptableSleep import InterruptableSleep
from ..util.Listeners import Listeners


class PriorityReceiveService(AbstractService, IReceiveListener, IReceiveService):
    def __init__(
            self,
            clock: IClock,
            receive_service: IReceiveService,
            service_manager: AbstractServiceManager,
            timeout_seconds: float,
    ) -> None:
        super().__init__(service_manager)
        self.current_priority = Atomic(0)
        self.interruptable_sleep = InterruptableSleep(clock)
        self.listeners: Listeners[IReceiveListener] = Listeners()
        self.should_run = True
        self.thread = Thread(target=self.run)
        self.timeout_seconds = timeout_seconds
        receive_service.add_receive_listener(self)

    def add_receive_listener(self, listener: IReceiveListener) -> PriorityReceiveService:
        self.listeners.add_listener(listener)
        return self

    def get_service_name(self) -> str:
        return __name__

    def join_service(self, timeout_seconds: Optional[float] = None) -> bool:
        self.thread.join(timeout_seconds)
        return self.thread.is_alive()

    def on_receive(self, message: bytes, details: ConnectionDetails) -> None:
        self.interruptable_sleep.interrupt()
        priority_message = PriorityMessage.decode(message)
        with self.current_priority as (current_priority, set_current_priority):
            if priority_message.priority > current_priority:
                set_current_priority(priority_message.priority)
            elif priority_message.priority < current_priority:
                return
        self.listeners.for_each(lambda listener: listener.on_receive(priority_message.payload, details))

    def run(self) -> None:
        while self.should_run:
            if self.interruptable_sleep.sleep(self.timeout_seconds) and self.should_run:
                with self.current_priority as (_, set_current_priority):
                    set_current_priority(0)

    def start_service(self) -> None:
        self.thread.start()

    def stop_service(self) -> None:
        self.should_run = False
        self.interruptable_sleep.interrupt()

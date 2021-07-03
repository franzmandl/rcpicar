from __future__ import annotations
from threading import Thread
from typing import Callable, Optional
from .interfaces import ITimeoutSendService
from ..clock import IClock
from ..service import IService, IServiceManager
from ..send import ISendService
from ..util.Atomic import Atomic
from ..util.InterruptableSleep import InterruptableSleep


class TimeoutSendService(IService, ITimeoutSendService):
    def __init__(
            self,
            clock: IClock,
            send_service: ISendService,
            service_manager: IServiceManager,
            timeout_seconds: float,
            message_callback: Callable[[], Optional[bytes]] = lambda: None,
    ) -> None:
        self.interruptable_sleep = InterruptableSleep(clock)
        self.timeout_seconds = timeout_seconds
        self.message_callback = Atomic(message_callback)
        self.send_count = 0
        self.send_service = send_service
        self.should_run = True
        self.thread = Thread(target=self.run)
        service_manager.add_service(self)

    def get_send_count(self) -> int:
        return self.send_count

    def get_service_name(self) -> str:
        return __name__

    def join_service(self, timeout_seconds: Optional[float] = None) -> bool:
        self.thread.join(timeout_seconds)
        return self.thread.is_alive()

    def run(self) -> None:
        should_send = True
        while self.should_run:
            if should_send:
                with self.message_callback as (message_callback, _):
                    self._send(message_callback())
            should_send = self.interruptable_sleep.sleep(self.timeout_seconds)

    def set_and_send_immediately(self, message_callback: Callable[[], Optional[bytes]]) -> Optional[bytes]:
        with self.message_callback as (_, set_message_callback):
            message = message_callback()
            self._send(message)
            set_message_callback(message_callback)
        self.interruptable_sleep.interrupt()
        return message

    def _send(self, message: Optional[bytes]) -> None:
        if message is not None:
            self.send_count += 1
            self.send_service.send(message)

    def start_service(self) -> None:
        self.thread.start()

    def stop_service(self) -> None:
        self.should_run = False
        self.interruptable_sleep.interrupt()

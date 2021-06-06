from __future__ import annotations
from threading import Event
from ..clock import IClock


class InterruptableSleep:
    """
    Inspired by https://stackoverflow.com/questions/24617131/is-there-a-graceful-or-pythonic-way-to-interrupt-a-time
    and https://stackoverflow.com/questions/16740104/python-lock-with-statement-and-timeout#16782391
    Also see https://docs.python.org/3/library/threading.html#threading.Event
    """
    def __init__(self, clock: IClock) -> None:
        self.clock = clock
        self.event = Event()

    def sleep(self, seconds: float) -> bool:
        """
        :return: True if slept through, False if sleep was interrupted.
        """
        self.event.clear()
        rv = not self.clock.wait_for_event(self.event, seconds)
        return rv

    def interrupt(self) -> None:
        self.event.set()

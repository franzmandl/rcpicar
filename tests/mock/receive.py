from __future__ import annotations
from typing import Tuple
from rcpicar.receive import IReceiveService, IReceiveListener
from rcpicar.util.ConnectionDetails import ConnectionDetails
from rcpicar.util.Listeners import Listeners
from tests.mock.helper import mock_details
from tests.suite.spy import FunctionSpy


class MockReceiveService(IReceiveService):
    class Tunnel:
        def __init__(self) -> None:
            self.mock = MockReceiveService()

            def add_receive_listener(args: Tuple[IReceiveListener]) -> IReceiveService:
                listener, = args
                self.receive_listeners.add_listener(listener)
                return self.mock

            self.mock.add_receive_listener_spy.callback(add_receive_listener)
            self.receive_listeners: Listeners[IReceiveListener] = Listeners()

        def send(self, message: bytes, details: ConnectionDetails = mock_details) -> None:
            self.receive_listeners.for_each(lambda listener: listener.on_receive(message, details))

    def __init__(self) -> None:
        self.add_receive_listener_spy: FunctionSpy[
            Tuple[IReceiveListener], IReceiveService] = FunctionSpy()

    def add_receive_listener(self, listener: IReceiveListener) -> IReceiveService:
        return self.add_receive_listener_spy((listener,))


class MockReceiveListener(IReceiveListener):
    @staticmethod
    def create_dummy() -> MockReceiveListener:
        mock = MockReceiveListener()
        mock.on_receive_spy.constant(None)
        return mock

    def __init__(self) -> None:
        self.on_receive_spy: FunctionSpy[Tuple[bytes, ConnectionDetails], None] = FunctionSpy()

    def on_receive(self, message: bytes, details: ConnectionDetails) -> None:
        self.on_receive_spy((message, details))

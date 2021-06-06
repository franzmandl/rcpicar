from __future__ import annotations
from typing import Tuple
from rcpicar.unreliable import IUnreliableOsErrorListener, IUnreliableReceiveListener
from rcpicar.util.ConnectionDetails import ConnectionDetails
from tests.suite.spy import FunctionSpy


class MockUnreliableOsErrorListener(IUnreliableOsErrorListener):
    @staticmethod
    def create_dummy() -> MockUnreliableOsErrorListener:
        mock = MockUnreliableOsErrorListener()
        mock.on_unreliable_os_error_spy.constant(None)
        return mock

    def __init__(self) -> None:
        self.on_unreliable_os_error_spy: FunctionSpy[Tuple[OSError], None] = FunctionSpy()

    def on_unreliable_os_error(self, os_error: OSError) -> None:
        self.on_unreliable_os_error_spy((os_error,))


class MockUnreliableReceiveListener(IUnreliableReceiveListener):
    @staticmethod
    def create_dummy() -> MockUnreliableReceiveListener:
        mock = MockUnreliableReceiveListener()
        mock.on_unreliable_receive_spy.constant(None)
        return mock

    def __init__(self) -> None:
        self.on_unreliable_receive_spy: FunctionSpy[Tuple[bytes, ConnectionDetails], None] = FunctionSpy()

    def on_unreliable_receive(self, message: bytes, details: ConnectionDetails) -> None:
        self.on_unreliable_receive_spy((message, details))

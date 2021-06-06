from __future__ import annotations
from typing import Tuple
from rcpicar.reliable import IReliableService, IReliableReceiveListener, IReliableOsErrorListener
from rcpicar.reliable import IReliableConnectListener, IReliableDisconnectListener
from rcpicar.util.ConnectionDetails import ConnectionDetails
from tests.suite.spy import FunctionSpy


class MockReliableService(IReliableService):
    @staticmethod
    def create_dummy() -> MockReliableService:
        mock = MockReliableService()
        mock.add_reliable_connect_listener_spy.constant(mock)
        mock.add_reliable_disconnect_listener_spy.constant(mock)
        mock.add_reliable_os_error_listener_spy.constant(mock)
        mock.add_reliable_receive_listener_spy.constant(mock)
        return mock

    def __init__(self) -> None:
        self.add_reliable_connect_listener_spy: FunctionSpy[
            Tuple[IReliableConnectListener], IReliableService] = FunctionSpy()
        self.add_reliable_disconnect_listener_spy: FunctionSpy[
            Tuple[IReliableDisconnectListener], IReliableService] = FunctionSpy()
        self.add_reliable_os_error_listener_spy: FunctionSpy[
            Tuple[IReliableOsErrorListener], IReliableService] = FunctionSpy()
        self.add_reliable_receive_listener_spy: FunctionSpy[
            Tuple[IReliableReceiveListener], IReliableService] = FunctionSpy()
        self.get_own_address_spy: FunctionSpy[Tuple[()], Tuple[str, int]] = FunctionSpy()

    def add_reliable_connect_listener(self, listener: IReliableConnectListener) -> IReliableService:
        return self.add_reliable_connect_listener_spy((listener,))

    def add_reliable_disconnect_listener(self, listener: IReliableDisconnectListener) -> IReliableService:
        return self.add_reliable_disconnect_listener_spy((listener,))

    def add_reliable_os_error_listener(self, listener: IReliableOsErrorListener) -> IReliableService:
        return self.add_reliable_os_error_listener_spy((listener,))

    def add_reliable_receive_listener(self, listener: IReliableReceiveListener) -> IReliableService:
        return self.add_reliable_receive_listener_spy((listener,))

    def get_own_address(self) -> Tuple[str, int]:
        return self.get_own_address_spy(())


class MockReliableConnectListener(IReliableConnectListener):
    @staticmethod
    def create_dummy() -> MockReliableConnectListener:
        mock = MockReliableConnectListener()
        mock.on_reliable_connect_spy.constant(None)
        return mock

    def __init__(self) -> None:
        self.on_reliable_connect_spy: FunctionSpy[Tuple[ConnectionDetails], None] = FunctionSpy()

    def on_reliable_connect(self, details: ConnectionDetails) -> None:
        self.on_reliable_connect_spy((details,))


class MockReliableDisconnectListener(IReliableDisconnectListener):
    @staticmethod
    def create_dummy() -> MockReliableDisconnectListener:
        mock = MockReliableDisconnectListener()
        mock.on_reliable_disconnect_spy.constant(None)
        return mock

    def __init__(self) -> None:
        self.on_reliable_disconnect_spy: FunctionSpy[Tuple[ConnectionDetails], None] = FunctionSpy()

    def on_reliable_disconnect(self, details: ConnectionDetails) -> None:
        self.on_reliable_disconnect_spy((details,))


class MockReliableOsErrorListener(IReliableOsErrorListener):
    @staticmethod
    def create_dummy() -> MockReliableOsErrorListener:
        mock = MockReliableOsErrorListener()
        mock.on_reliable_os_error_spy.constant(None)
        return mock

    def __init__(self) -> None:
        self.on_reliable_os_error_spy: FunctionSpy[Tuple[OSError], None] = FunctionSpy()

    def on_reliable_os_error(self, os_error: OSError) -> None:
        self.on_reliable_os_error_spy((os_error,))


class MockReliableReceiveListener(IReliableReceiveListener):
    @staticmethod
    def create_dummy() -> MockReliableReceiveListener:
        mock = MockReliableReceiveListener()
        mock.on_reliable_receive_spy.constant(None)
        return mock

    def __init__(self) -> None:
        self.on_reliable_receive_spy: FunctionSpy[Tuple[bytes, ConnectionDetails], None] = FunctionSpy()

    def on_reliable_receive(self, message: bytes, details: ConnectionDetails) -> None:
        self.on_reliable_receive_spy((message, details))

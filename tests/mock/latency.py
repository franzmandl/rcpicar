from __future__ import annotations
from typing import Tuple
from rcpicar.latency.interfaces import ILatencyListener, ILatencyServerService
from tests.suite.spy import FunctionSpy


class MockLatencyServerService(ILatencyServerService):
    @staticmethod
    def create_dummy() -> MockLatencyServerService:
        mock = MockLatencyServerService()
        mock.add_latency_listener_spy.constant(mock)
        return mock

    def __init__(self) -> None:
        self.add_latency_listener_spy: FunctionSpy[Tuple[ILatencyListener], ILatencyServerService] = FunctionSpy()

    def add_latency_listener(self, latency_listener: ILatencyListener) -> ILatencyServerService:
        return self.add_latency_listener_spy((latency_listener,))

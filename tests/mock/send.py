from __future__ import annotations
from typing import Tuple
from rcpicar.send import ISendService
from tests.suite.spy import FunctionSpy


class MockSendService(ISendService):
    @staticmethod
    def create_dummy() -> MockSendService:
        mock = MockSendService()
        mock.send_spy.constant(None)
        return mock

    def __init__(self) -> None:
        self.send_spy: FunctionSpy[Tuple[bytes], None] = FunctionSpy()

    def send(self, message: bytes) -> None:
        self.send_spy((message,))

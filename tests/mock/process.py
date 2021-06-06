from __future__ import annotations
from types import TracebackType
from typing import Optional, Sequence, IO, Iterator, Iterable, Tuple, Type
from rcpicar.process import IProcess, FILE
from tests.suite.spy import fail_no_mock, FunctionSpy


class MockIO(IO[bytes]):
    def __init__(self) -> None:
        self.readline_spy: FunctionSpy[Tuple[int], bytes] = FunctionSpy()

    def close(self) -> None:
        fail_no_mock()

    def fileno(self) -> int:
        return fail_no_mock()

    def flush(self) -> None:
        fail_no_mock()

    def isatty(self) -> bool:
        return fail_no_mock()

    def read(self, n: int = -1) -> bytes:
        return fail_no_mock()

    def readable(self) -> bool:
        return fail_no_mock()

    def readline(self, limit: int = -1) -> bytes:
        return self.readline_spy((limit,))

    def readlines(self, hint: int = -1) -> list[bytes]:
        return fail_no_mock()

    def seek(self, offset: int, whence: int = 0) -> int:
        return fail_no_mock()

    def seekable(self) -> bool:
        return fail_no_mock()

    def tell(self) -> int:
        return fail_no_mock()

    def truncate(self, size: Optional[int] = None) -> int:
        return fail_no_mock()

    def writable(self) -> bool:
        return fail_no_mock()

    def write(self, s: bytes) -> int:
        return fail_no_mock()

    def writelines(self, lines: Iterable[bytes]) -> None:
        fail_no_mock()

    def __next__(self) -> bytes:
        return fail_no_mock()

    def __iter__(self) -> Iterator[bytes]:
        return fail_no_mock()

    def __enter__(self) -> IO[bytes]:
        return fail_no_mock()

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType]
    ) -> Optional[bool]:
        return fail_no_mock()


class MockProcess(IProcess):
    @staticmethod
    def create_dummy() -> MockProcess:
        mock = MockProcess()
        mock.terminate_spy.constant(None)
        mock.wait_spy.constant(None)
        return mock

    def __init__(self) -> None:
        self.get_stdout_spy: FunctionSpy[Tuple[()], IO[bytes]] = FunctionSpy()
        self.terminate_spy: FunctionSpy[Tuple[()], None] = FunctionSpy()
        self.wait_spy: FunctionSpy[Tuple[Optional[float]], None] = FunctionSpy()

    def get_stdout(self) -> IO[bytes]:
        return self.get_stdout_spy(())

    def terminate(self) -> None:
        return self.terminate_spy(())

    def wait(self, timeout: Optional[float]) -> None:
        return self.wait_spy((timeout,))


class MockProcessFactory:
    def __init__(self) -> None:
        self.call___spy: FunctionSpy[
            Tuple[Sequence[str], Optional[FILE], Optional[FILE]], IProcess] = FunctionSpy()

    def __call__(self, args: Sequence[str], stdin: Optional[FILE], stdout: Optional[FILE]) -> IProcess:
        return self.call___spy((args, stdin, stdout))

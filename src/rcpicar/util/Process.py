from subprocess import Popen
from typing import IO, Optional, Sequence
from ..process import FILE, IProcess


class Process(IProcess):
    def __init__(self, args: Sequence[str], stdin: Optional[FILE], stdout: Optional[FILE]) -> None:
        self.process = Popen(args, stdin=stdin, stdout=stdout)

    def get_stdout(self) -> IO[bytes]:
        if self.process.stdout is None:
            raise RuntimeError('Unexpected None. Is stdout set to PIPE?')
        return self.process.stdout

    def terminate(self) -> None:
        self.process.terminate()

    def wait(self, timeout: Optional[float]) -> None:
        self.process.wait(timeout)

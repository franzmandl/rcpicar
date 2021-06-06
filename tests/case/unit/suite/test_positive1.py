from __future__ import annotations
from typing import Generator, Optional, Tuple
from tests.suite.spy import FunctionSpy


def generator() -> Generator[str, None, None]:
    yield 'ITERATOR1'
    yield 'ITERATOR2'


class Mocked:
    def __init__(self) -> None:
        self.value = 'SELF'
        self.callback_spy: FunctionSpy[Tuple[str, str], str] = FunctionSpy()
        self.constant1_spy: FunctionSpy[Tuple[()], Optional[str]] = FunctionSpy()
        self.constant2_spy: FunctionSpy[Tuple[()], str] = FunctionSpy()
        self.constant3_spy: FunctionSpy[Tuple[()], str] = FunctionSpy()
        self.iterable_spy: FunctionSpy[Tuple[()], str] = FunctionSpy()
        self.range_spy: FunctionSpy[Tuple[()], int] = FunctionSpy()
        self.iterator_spy: FunctionSpy[Tuple[()], str] = FunctionSpy()

    def callback(self, a: str, b: str) -> str:
        return self.callback_spy((a, b))

    def constant1(self) -> Optional[str]:
        return self.constant1_spy(())

    def constant2(self) -> str:
        return self.constant2_spy(())

    def constant3(self) -> str:
        return self.constant3_spy(())

    def iterable(self) -> str:
        return self.iterable_spy(())

    def iterator(self) -> str:
        return self.iterator_spy(())

    def range(self) -> int:
        return self.range_spy(())

    def no_spy(self) -> str:
        return f'{self.value}_NO_SPY'


def test() -> None:
    # given
    mocked = Mocked()

    def callback(args: Tuple[str, str]) -> str:
        arg1, arg2 = args
        return f'CALLBACK_{arg1}_{arg2}'

    # when
    mocked.callback_spy.callback(callback)
    mocked.constant1_spy.constant(None)
    mocked.constant2_spy.constant('CONSTANT2')
    mocked.constant3_spy.constant('CONSTANT3')
    mocked.iterable_spy.iterable(['ITERABLE1', 'ITERABLE2'])
    mocked.range_spy.iterable(range(1, 3))
    mocked.iterator_spy.iterator(generator())
    # then
    assert mocked.no_spy() == 'SELF_NO_SPY'
    assert mocked.callback('ARG11', 'ARG12') == 'CALLBACK_ARG11_ARG12'
    assert mocked.callback('ARG21', 'ARG22') == 'CALLBACK_ARG21_ARG22'
    assert mocked.callback_spy.get_times_called() == 2
    assert mocked.callback_spy.get_called_args() == [('ARG11', 'ARG12'), ('ARG21', 'ARG22')]
    assert mocked.constant1() is None
    assert mocked.constant1() is None
    assert mocked.constant1_spy.get_times_called() == 2
    assert mocked.constant1_spy.get_called_args() == [(), ()]
    assert mocked.constant2() == 'CONSTANT2'
    assert mocked.constant2() == 'CONSTANT2'
    assert mocked.constant2() == 'CONSTANT2'
    assert mocked.constant2_spy.get_times_called() == 3
    assert mocked.constant2_spy.get_called_args() == [(), (), ()]
    assert mocked.constant3() == 'CONSTANT3'
    assert mocked.constant3_spy.get_times_called() == 1
    assert mocked.constant3_spy.get_called_args() == [()]
    assert mocked.iterable() == 'ITERABLE1'
    assert mocked.iterable() == 'ITERABLE2'
    assert mocked.iterable_spy.get_times_called() == 2
    assert mocked.iterable_spy.get_called_args() == [(), ()]
    assert mocked.range() == 1
    assert mocked.range() == 2
    assert mocked.range_spy.get_times_called() == 2
    assert mocked.range_spy.get_called_args() == [(), ()]
    assert mocked.iterator() == 'ITERATOR1'
    assert mocked.iterator() == 'ITERATOR2'
    assert mocked.iterator_spy.get_times_called() == 2
    assert mocked.iterator_spy.get_called_args() == [(), ()]


if __name__ == '__main__':
    test()

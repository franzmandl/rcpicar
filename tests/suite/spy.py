from __future__ import annotations
from abc import ABC, abstractmethod
from pytest import fail
from threading import Condition
from typing import Callable, Generic, Iterable, Iterator, List, Mapping, NoReturn, Optional, TypeVar

AT = TypeVar('AT')
RT = TypeVar('RT')


def fail_no_mock() -> NoReturn:
    fail('No mock specified')


class CallResultEntry(Generic[AT, RT]):
    def __init__(self, args: AT, exception: Optional[BaseException], return_value: Optional[RT]) -> None:
        self.args = args
        self.exception = exception
        self.return_value = return_value


class IMock(Generic[AT, RT], ABC):
    @abstractmethod
    def mock(self, args: AT) -> RT:
        """"""


class CallbackFunctionMock(Generic[AT, RT], IMock[AT, RT]):
    def __init__(self, callback: Callable[[AT], RT]) -> None:
        self.callback = callback

    def mock(self, args: AT) -> RT:
        return self.callback(args)


class ConstantFunctionMock(Generic[AT, RT], IMock[AT, RT]):
    def __init__(self, constant: RT) -> None:
        self.constant = constant

    def mock(self, args: AT) -> RT:
        return self.constant


class ExceptionFunctionMock(Generic[AT, RT], IMock[AT, RT]):
    def __init__(self, exception: BaseException) -> None:
        self.exception = exception

    def mock(self, args: AT) -> RT:
        raise self.exception


class FailFunctionMock(Generic[AT, RT], IMock[AT, RT]):
    def mock(self, args: AT) -> RT:
        return fail_no_mock()


class IteratorFunctionMock(Generic[AT, RT], IMock[AT, RT]):
    def __init__(self, iterator: Iterator[RT]) -> None:
        self.iterator = iterator

    def mock(self, args: AT) -> RT:
        return next(self.iterator)


class MappingFunctionMock(Generic[AT, RT], IMock[AT, RT]):
    def __init__(self, dict_: Mapping[AT, RT]) -> None:
        self.dict = dict_

    def mock(self, args: AT) -> RT:
        if args not in self.dict:
            fail_no_mock()
        return self.dict[args]


class FunctionSpy(Generic[AT, RT]):
    def __init__(self) -> None:
        self.consumed_called_args_count = 0
        self.consumed_times_called_count = 0
        self.called_args: List[AT] = []
        self.called_args_cv = Condition()
        self.call_results: List[CallResultEntry[AT, RT]] = []
        self.mock: IMock[AT, RT] = FailFunctionMock()

    def callback(self, callback: Callable[[AT], RT]) -> FunctionSpy[AT, RT]:
        self.mock = CallbackFunctionMock(callback)
        return self

    def constant(self, constant: RT) -> FunctionSpy[AT, RT]:
        self.mock = ConstantFunctionMock(constant)
        return self

    def exception(self, exception: BaseException) -> FunctionSpy[AT, RT]:
        self.mock = ExceptionFunctionMock(exception)
        return self

    def iterable(self, iterable: Iterable[RT]) -> FunctionSpy[AT, RT]:
        self.mock = IteratorFunctionMock(iter(iterable))
        return self

    def iterator(self, iterable: Iterator[RT]) -> FunctionSpy[AT, RT]:
        self.mock = IteratorFunctionMock(iterable)
        return self

    def mapping(self, mapping: Mapping[AT, RT]) -> FunctionSpy[AT, RT]:
        self.mock = MappingFunctionMock(mapping)
        return self

    def __call__(self, args: AT) -> RT:
        with self.called_args_cv:
            self.called_args.append(args)
            self.called_args_cv.notify()
        try:
            return_value = self.mock.mock(args)
            self.call_results.append(CallResultEntry(args, None, return_value))
            return return_value
        except BaseException as exception:
            self.call_results.append(CallResultEntry(args, exception, None))
            raise exception

    def wait_for_call(self) -> None:
        self.wait_for_calls(1)

    def wait_for_calls(self, count: int) -> None:
        new_consumed_times_called_count = self.consumed_times_called_count + count
        self.wait_till_have_been_times_called(new_consumed_times_called_count)
        self.consumed_times_called_count = new_consumed_times_called_count

    def wait_till_have_been_times_called(self, count: int) -> None:
        with self.called_args_cv:
            self.called_args_cv.wait_for(lambda: len(self.called_args) >= count)

    def get_called_args(self) -> List[AT]:
        return self.called_args

    def consume_called_args(self) -> List[AT]:
        old_consumed_called_args_count = self.consumed_called_args_count
        new_consumed_called_args_count = len(self.called_args)
        self.consumed_called_args_count = new_consumed_called_args_count
        return self.called_args[old_consumed_called_args_count:new_consumed_called_args_count]

    def get_times_called(self) -> int:
        return len(self.called_args)

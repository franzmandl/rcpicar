from typing import Any, Tuple, Type, TypeVar
from ..constants import buffer_size

V1 = TypeVar('V1')
V2 = TypeVar('V2')


class BufferSizeExceededError(RuntimeError):
    def __init__(self, length: int) -> None:
        super().__init__(f'Buffer size exceeded: {length} > {buffer_size}')


def check_message_length(length: int) -> None:
    if length > buffer_size:
        raise BufferSizeExceededError(length)


class UnexpectedTypeError(TypeError):
    def __init__(self, subject: Any, expected: str) -> None:
        super().__init__(f'Expected type {expected}, got {subject}')


def check_type(subject: Any, type_: Type[V1]) -> V1:
    if not isinstance(subject, type_):
        raise UnexpectedTypeError(subject, str(type_))
    return subject


def check_type_tuple2(subject: Any, type1: Type[V1], type2: Type[V2]) -> Tuple[V1, V2]:
    def create_error() -> UnexpectedTypeError:
        return UnexpectedTypeError(subject, f'({type1}, {type2})')

    if not isinstance(subject, tuple):
        raise create_error()
    if not len(subject) == 2:
        raise create_error()
    value1, value2 = subject
    if not isinstance(value1, type1):
        raise create_error()
    if not isinstance(value2, type2):
        raise create_error()
    return value1, value2

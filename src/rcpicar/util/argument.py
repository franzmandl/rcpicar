from __future__ import annotations
from abc import ABC, abstractmethod
from argparse import ArgumentParser, MetavarTypeHelpFormatter
from sys import version_info
from typing import Any, Callable, Dict, Generic, Iterable, Mapping, Optional, Sequence, Tuple, Type, TypeVar
if version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict
from .checking import check_type
from .Lazy import Lazy

K = TypeVar('K')
T = TypeVar('T')
ParsedType = TypeVar('ParsedType')


def get_key_of_value(haystack: Mapping[K, T], needle: T) -> K:
    for key, value in haystack.items():
        if needle == value:
            return key
    raise RuntimeError(f'Value "{needle}" not found in mapping.')


class AddArgumentKwargs(TypedDict, total=False):
    dest: str
    help: str
    type: Type[Any]


AddArgumentArgs = Tuple[str]


class IArgument(Generic[ParsedType], ABC):
    @abstractmethod
    def add_argument(self, parser: ArgumentParser) -> None:
        """"""

    @abstractmethod
    def get_name(self) -> str:
        """"""

    @abstractmethod
    def set_value(self, value: ParsedType) -> None:
        """"""


AnyArgument = IArgument[Any]
AnyArguments = Iterable[AnyArgument]


class IArguments(ABC):
    def get_arguments(self) -> AnyArguments:
        return []


class Argument(Generic[T, ParsedType], IArgument[ParsedType], IArguments):
    def __init__(
            self,
            parser_add_argument: Callable[[ArgumentParser, AddArgumentArgs, AddArgumentKwargs], None],
            default: Optional[str],
            help_: str,
            lazy: Lazy[T],
            name: str,
            parse_value: Callable[[ParsedType], T],
            type_: Type[ParsedType],
    ) -> None:
        self.parser_add_argument = parser_add_argument
        self.help = help_ if default is None else f'{help_} (default: {default or lazy.get_default()})'
        self.lazy = lazy
        self.name = name
        self.parse_value = parse_value
        self.type = type_

    def add_argument(self, parser: ArgumentParser) -> None:
        kwargs = AddArgumentKwargs()
        if self.name[0] in parser.prefix_chars:
            kwargs['dest'] = self.name
        kwargs['help'] = self.help
        kwargs['type'] = self.type
        self.parser_add_argument(parser, (self.name,), kwargs)

    def get_arguments(self) -> AnyArguments:
        return [self]

    def get_name(self) -> str:
        return self.name

    def set_value(self, value: ParsedType) -> None:
        self.lazy.set(self.parse_value(check_type(value, self.type)))


def create_choice_argument(
        lazy: Lazy[T],
        name: str,
        choices: Mapping[str, T],
        help_: str = '',
        default: str = ''
) -> Argument[T, str]:
    def add_argument(parser: ArgumentParser, args: AddArgumentArgs, kwargs: AddArgumentKwargs) -> None:
        parser.add_argument(*args, **kwargs, choices=choices)

    return Argument(
        add_argument, default or get_key_of_value(choices, lazy.get_default()),
        help_, lazy, name, lambda value: choices[value], str,
    )


def create_value_argument(
        lazy: Lazy[T],
        name: str,
        type_: Type[T],
        help_: str = '',
        default: Optional[str] = '',
) -> Argument[T, T]:
    def add_argument(parser: ArgumentParser, args: AddArgumentArgs, kwargs: AddArgumentKwargs) -> None:
        parser.add_argument(*args, **kwargs)

    return Argument(add_argument, default, help_, lazy, name, lambda value: value, type_)


class ArgumentRegistry:
    def __init__(self) -> None:
        self.parser = ArgumentParser(formatter_class=MetavarTypeHelpFormatter)
        self.arguments: Dict[str, AnyArgument] = dict()

    def add_arguments(self, arguments_list: Iterable[IArguments]) -> None:
        for arguments in arguments_list:
            for argument in arguments.get_arguments():
                self.add_argument(argument)

    def add_argument(self, argument: AnyArgument) -> None:
        name = argument.get_name()
        if name in self.arguments:
            raise RuntimeError(f'Argument {name} already used.')
        self.arguments[name] = argument
        argument.add_argument(self.parser)

    def parse_arguments(self, argument_vector: Optional[Sequence[str]] = None) -> None:
        parsed = vars(self.parser.parse_args(argument_vector))
        parsed_keys = set(parsed.keys())
        for name, value in parsed.items():
            if name not in self.arguments:
                raise RuntimeError(f'Unknown argument {name}.')
            if value is not None:
                self.arguments[name].set_value(value)
            parsed_keys.remove(name)
        if len(parsed_keys) != 0:
            unknown_arguments_string = ', '.join((f'{key}: {parsed[key]}' for key in parsed_keys))
            raise RuntimeError(f'Unknown arguments: {unknown_arguments_string}')


def process_arguments(arguments_list: Iterable[IArguments], argument_vector: Optional[Sequence[str]] = None) -> None:
    argument_registry = ArgumentRegistry()
    argument_registry.add_arguments(arguments_list)
    argument_registry.parse_arguments(argument_vector)

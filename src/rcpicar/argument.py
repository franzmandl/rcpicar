from __future__ import annotations
from abc import ABC, abstractmethod
from argparse import ArgumentParser, MetavarTypeHelpFormatter
from sys import version_info
from typing import Any, Dict, Generic, Iterable, Mapping, Optional, Sequence, Type, TypeVar
if version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict
from .util.checking import check_type
from .util.Lazy import Lazy

K = TypeVar('K')
T = TypeVar('T')
ParsedType = TypeVar('ParsedType')


def get_key_of_value(haystack: Mapping[K, T], needle: T) -> K:
    for key, value in haystack.items():
        if needle == value:
            return key
    raise RuntimeError(f'Value "{needle}" not found in mapping.')


class AddArgumentKwargs(TypedDict, total=False):
    choices: Iterable[Any]
    dest: str
    help: str
    type: Type[Any]


class IArguments(ABC):
    def get_arguments(self) -> AnyArguments:
        return []


class AbstractArgument(Generic[T, ParsedType], IArguments, ABC):
    def __init__(
            self, lazy: Lazy[T], name: str, type_: Type[ParsedType], help_: str = '', default: Optional[str] = ''
    ) -> None:
        self.help = help_ if default is None else f'{help_} (default: {default or lazy.get_default()})'
        self.lazy = lazy
        self.name = name
        self.type = type_

    def get_kwargs_for_add_argument(self) -> AddArgumentKwargs:
        return dict()

    def add_argument(self, parser: ArgumentParser) -> None:
        kwargs = self.get_kwargs_for_add_argument()
        if self.name[0] in parser.prefix_chars:
            kwargs['dest'] = self.name
        kwargs['help'] = self.help
        kwargs['type'] = self.type
        parser.add_argument(self.name, **kwargs)

    @abstractmethod
    def parse_value(self, value: ParsedType) -> T:
        """"""

    def get_arguments(self) -> AnyArguments:
        return [self]


AnyArgument = AbstractArgument[Any, Any]
AnyArguments = Iterable[AnyArgument]


class ChoiceArgument(Generic[T], AbstractArgument[T, str]):
    def __init__(self, lazy: Lazy[T], name: str, choices: Mapping[str, T], help_: str = '', default: str = '') -> None:
        super().__init__(lazy, name, str, help_, default or get_key_of_value(choices, lazy.get_default()))
        self.choices = choices

    def get_kwargs_for_add_argument(self) -> AddArgumentKwargs:
        return dict(choices=self.choices)

    def parse_value(self, value: str) -> T:
        return self.choices[check_type(value, self.type)]


class ValueArgument(Generic[T], AbstractArgument[T, T]):
    def parse_value(self, value: T) -> T:
        return check_type(value, self.type)


class ArgumentRegistry:
    def __init__(self) -> None:
        self.parser = ArgumentParser(formatter_class=MetavarTypeHelpFormatter)
        self.arguments: Dict[str, AbstractArgument[Any, Any]] = {}

    def add_arguments(self, arguments_list: Iterable[IArguments]) -> None:
        for arguments in arguments_list:
            for argument in arguments.get_arguments():
                self.add_argument(argument)

    def add_argument(self, argument: AbstractArgument[T, ParsedType]) -> None:
        name = argument.name
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
                argument = self.arguments[name]
                argument.lazy.set(argument.parse_value(value))
            parsed_keys.remove(name)
        if len(parsed_keys) != 0:
            unknown_arguments_string = ', '.join((f'{key}: {parsed[key]}' for key in parsed_keys))
            raise RuntimeError(f'Unknown arguments: {unknown_arguments_string}')
        for argument in self.arguments.values():
            argument.lazy.get()


def process_arguments(arguments_list: Iterable[IArguments], argument_vector: Optional[Sequence[str]] = None) -> None:
    argument_registry = ArgumentRegistry()
    argument_registry.add_arguments(arguments_list)
    argument_registry.parse_arguments(argument_vector)

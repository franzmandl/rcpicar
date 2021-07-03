#!/usr/bin/env python3
from glob import glob
from os import chdir, listdir, unlink
from os.path import basename, dirname, isdir, isfile, join, realpath
from re import search
from subprocess import run
from sys import argv
from typing import Callable, Generator, Iterable, Mapping, Sequence, Set


def get_file_content(path: str) -> str:
    with open(path) as file:
        return file.read()


def get_file_lines(path: str) -> Sequence[str]:
    return get_file_content(path).splitlines()


def walk(
        path: str,
        yield_predicate: Callable[[str], bool],
        prune_predicate: Callable[[str], bool],
) -> Generator[str, None, None]:
    if not prune_predicate(path):
        if yield_predicate(path):
            yield path
        if isdir(path):
            for child_name in listdir(path):
                yield from walk(join(path, child_name), yield_predicate, prune_predicate)


def prune_excluded(path: str) -> bool:
    return path.startswith(join('.', '.')) or path in {
        join('.', 'build'), join('.', 'dist'), join('.', 'venv')} or basename(path) == '__pycache__'


def is_code_file(path: str) -> bool:
    return isfile(path) and (path.endswith('.py') or path.endswith('.pyi'))


def get_dist_files() -> Iterable[str]:
    return filter(isfile, glob(join('.', 'dist', '*')))


def assert_run(args: Sequence[str]) -> None:
    print('$', *args)
    return_code = run(args).returncode
    if return_code != 0:
        raise SystemExit(return_code)


def assert_file_name(path: str, pattern: str, prune_predicate: Callable[[str], bool] = lambda _: False) -> None:
    print(f'> Checking file names not matching "{pattern}"')
    found_violation = False
    for matched_path in walk(path, is_code_file, prune_predicate):
        if not search(pattern, matched_path):
            found_violation = True
            print(f'Found violation: "{matched_path}"')
    if found_violation:
        raise SystemExit(1)


def assert_file_line(path: str, pattern: str, prune_predicate: Callable[[str], bool] = lambda _: False) -> None:
    print(f'> Checking file lines for "{pattern}"')
    found_violation = False
    for matched_path in walk(path, is_code_file, prune_predicate):
        for index, line in enumerate(get_file_lines(matched_path)):
            match = search(pattern, line)
            if match:
                found_violation = True
                print(f'Found violation: "{matched_path}:{index + 1}:{match.pos + 1}"')
    if found_violation:
        raise SystemExit(1)


def resolve_dependencies(flat_dependencies: Set[str], all_dependencies: Mapping[str, Set[str]]) -> Set[str]:
    resolved_dependencies = flat_dependencies.copy()
    for dependency in flat_dependencies:
        if dependency in all_dependencies:
            resolved_dependencies |= resolve_dependencies(all_dependencies[dependency], all_dependencies)
    return resolved_dependencies


def main() -> None:
    chdir(dirname(realpath(__file__)))
    goals = resolve_dependencies(set(argv[1:]) or {'build'}, {
        'build': {'test'},
        'check': {'check_style', 'check_type'},
        'test': {'check'},
        'upload': {'build'},
        'upload-test': {'build'},
    })
    if 'venv' in goals:
        assert_run(['python3', '-m', 'venv', '--system-site-packages', join('.', 'venv')])
    if 'check_type' in goals:
        assert_run(['python3', '-m', 'mypy'])
        assert_file_line('.', '    def __init__\\(self, .*\\):$', prune_excluded)
        assert_file_line('.', '    \\):$', prune_excluded)
    if 'check_style' in goals:
        assert_run(['python3', '-m', 'pycodestyle'])
        assert_file_name(join('.', 'stubs'), '^.*\\.pyi$')
        assert_file_line(join('.', 'stubs'), '    pass$')
    if isdir(join('.', 'tests')) and 'test' in goals:
        assert_run(['python3', '-m', 'pytest'])
    if 'build' in goals:
        for file_path in get_dist_files():
            unlink(file_path)
        assert_run(['python3', '-m', 'build'])
    if 'upload-test' in goals:
        assert_run(['python3', '-m', 'twine', 'upload', '--repository', 'testpypi'] + list(get_dist_files()))
    if 'upload' in goals:
        assert_run(['python3', '-m', 'twine', 'upload'] + list(get_dist_files()))
    print('SUCCESS')


if __name__ == '__main__':
    main()

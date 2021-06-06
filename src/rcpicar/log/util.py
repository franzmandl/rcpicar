from __future__ import annotations
from logging import basicConfig, FileHandler, Formatter, Logger, StreamHandler
from typing import Callable, Optional, TypeVar

RV = TypeVar('RV')


def configure_log(log_file: Optional[str], log_level: int) -> None:
    formatter = Formatter(f'%(levelname)-5.5s:%(asctime)s:%(threadName)s:%(name)s:%(message)s')
    handlers = [StreamHandler()]
    if log_file is not None:
        handlers.append(FileHandler(log_file))
    for handler in handlers:
        handler.setFormatter(formatter)
    basicConfig(level=log_level, handlers=handlers)


def log_method_call(logger: Logger, method: Callable[[], RV]) -> Callable[[], RV]:
    def decorator() -> RV:
        try:
            logger.debug(f'entering {method.__name__}()')
            return method()
        finally:
            logger.debug(f'leaving {method.__name__}()')
    return decorator

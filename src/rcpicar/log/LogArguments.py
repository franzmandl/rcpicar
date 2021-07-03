from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING
from .util import configure_log
from ..util.argument import AnyArguments, create_choice_argument, create_value_argument, IArguments
from ..util.Lazy import Lazy


class LogArguments(IArguments):
    def __init__(self) -> None:
        self.log_file = Lazy(lambda store: None)
        self.log_level = Lazy(lambda store: WARNING)

    def configure_log(self) -> None:
        configure_log(self.log_file.get(), self.log_level.get())

    def get_arguments(self) -> AnyArguments:
        return [
            create_value_argument(
                self.log_file, '--log-file', str, 'Gets created if does not exists. Gets appended if exists.'),
            create_choice_argument(self.log_level, '--log-level', {
                'debug': DEBUG,
                'info': INFO,
                'warn': WARNING,
                'error': ERROR,
                'critical': CRITICAL,
            }, 'Verbosity of the log output.')
        ]

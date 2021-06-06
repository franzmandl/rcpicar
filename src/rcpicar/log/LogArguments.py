from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING
from ..argument import AnyArguments, ChoiceArgument, IArguments, ValueArgument
from ..util.Lazy import Lazy


class LogArguments(IArguments):
    def __init__(self) -> None:
        self.log_file = Lazy(lambda store: None)
        self.log_level = Lazy(lambda store: WARNING)

    def get_arguments(self) -> AnyArguments:
        return [
            ValueArgument(
                self.log_file, '--log-file', str, 'Gets created if does not exists. Gets appended if exists.'),
            ChoiceArgument(self.log_level, '--log-level', {
                'debug': DEBUG,
                'info': INFO,
                'warn': WARNING,
                'error': ERROR,
                'critical': CRITICAL,
            }, 'Verbosity of the log output.')
        ]

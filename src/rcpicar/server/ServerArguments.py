from ..constants import default_server_port
from ..util.argument import AnyArguments, create_value_argument, IArguments
from ..util.Lazy import Lazy


class ServerArguments(IArguments):
    def __init__(self) -> None:
        self.listen_ip = Lazy(lambda store: '0.0.0.0')
        self.listen_port = Lazy(lambda store: default_server_port)
        self.listen_address = Lazy(lambda store: (self.listen_ip(store), self.listen_port(store)))
        self.priority_timeout_seconds = Lazy(lambda store: 1.0)
        self.unreliable_timeout_seconds = Lazy(lambda store: 60.0)

    def get_arguments(self) -> AnyArguments:
        return [
            create_value_argument(self.listen_ip, '--listen-ip', str, 'TCP/UDP listen IP.'),
            create_value_argument(self.listen_port, '--listen-port', int, 'TCP/UDP listen port.'),
            create_value_argument(
                self.unreliable_timeout_seconds, '--unreliable-timeout-seconds', float,
                'Stop sending unreliable messages to last known client after receiving nothing for this amount of '
                'seconds.'
            ),
        ]

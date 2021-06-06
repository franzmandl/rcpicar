from ..argument import AnyArguments, IArguments, ValueArgument
from ..constants import default_server_port, discover_server_ip
from ..util.Lazy import Lazy


class ClientArguments(IArguments):
    def __init__(self) -> None:
        self.reconnect_seconds = Lazy(lambda store: 1.0)
        self.server_ip = Lazy(lambda store: discover_server_ip)
        self.server_port = Lazy(lambda store: default_server_port)
        self.server_address = Lazy(lambda store: (self.server_ip(store), self.server_port(store)))

    def get_arguments(self) -> AnyArguments:
        return [
            ValueArgument(self.server_ip, '--server-ip', str, 'TCP/UDP server IP.'),
            ValueArgument(self.server_port, '--server-port', int, 'TCP/UDP server port.'),
        ]

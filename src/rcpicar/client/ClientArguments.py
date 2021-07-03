from ..constants import default_server_port, discover_server_ip
from ..util.argument import AnyArguments, create_value_argument, IArguments
from ..util.Lazy import Lazy


class ClientArguments(IArguments):
    def __init__(self) -> None:
        self.priority = Lazy(lambda store: 128)
        self.reconnect_seconds = Lazy(lambda store: 1.0)
        self.send_timeout_seconds = Lazy(lambda store: 0.125)
        self.server_ip = Lazy(lambda store: discover_server_ip)
        self.server_port = Lazy(lambda store: default_server_port)
        self.server_address = Lazy(lambda store: (self.server_ip(store), self.server_port(store)))

    def get_arguments(self) -> AnyArguments:
        return [
            create_value_argument(self.priority, '--priority', int, 'Priority of client.'),
            create_value_argument(self.server_ip, '--server-ip', str, 'TCP/UDP server IP.'),
            create_value_argument(self.server_port, '--server-port', int, 'TCP/UDP server port.'),
        ]

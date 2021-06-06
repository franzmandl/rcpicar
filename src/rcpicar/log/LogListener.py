from __future__ import annotations
from logging import getLogger
from ..latency.ILatencyListener import ILatencyListener
from ..receive import IReceiveListener
from ..reliable import IReliableConnectListener, IReliableDisconnectListener, IReliableOsErrorListener
from ..reliable import IReliableReceiveListener
from ..routed.IRoutedReceiveListener import IRoutedReceiveListener
from ..unreliable import IUnreliableOsErrorListener, IUnreliableReceiveListener
from ..timeout.ITimeoutReceiveListener import ITimeoutReceiveListener
from ..util.ConnectionDetails import ConnectionDetails


class LogListener(
    ILatencyListener,
    IReceiveListener,
    IReliableConnectListener,
    IReliableDisconnectListener,
    IReliableOsErrorListener,
    IReliableReceiveListener,
    IRoutedReceiveListener,
    IUnreliableOsErrorListener,
    IUnreliableReceiveListener,
    ITimeoutReceiveListener,
):
    def __init__(self) -> None:
        self.logger = getLogger(__name__)

    def on_latency_available(self, latency: float) -> None:
        self.logger.info(f'on_latency_available({latency})')

    def on_latency_timeout(self) -> None:
        self.logger.info(f'on_latency_timeout()')

    def on_receive(self, message: bytes, details: ConnectionDetails) -> None:
        self.logger.info(f'on_received({message!r}, {details})')

    def on_routed_receive(self, message_type: int, message: bytes, details: ConnectionDetails) -> None:
        self.logger.info(f'on_routed_receive({message_type}, {message!r}, {details})')

    def on_timeout_receive(self) -> None:
        self.logger.info('on_receive_timeout')

    def on_reliable_connect(self, details: ConnectionDetails) -> None:
        self.logger.info(f'on_reliable_connected({details})')

    def on_reliable_disconnect(self, details: ConnectionDetails) -> None:
        self.logger.info(f'on_reliable_disconnected({details})')

    def on_reliable_os_error(self, os_error: OSError) -> None:
        self.logger.info(f'on_reliable_os_error({os_error})')

    def on_reliable_receive(self, message: bytes, details: ConnectionDetails) -> None:
        self.logger.info(f'on_reliable_received({message!r}, {details})')

    def on_unreliable_os_error(self, os_error: OSError) -> None:
        self.logger.info(f'on_unreliable_os_error({os_error})')

    def on_unreliable_receive(self, message: bytes, details: ConnectionDetails) -> None:
        self.logger.info(f'on_unreliable_received({message!r}, {details})')

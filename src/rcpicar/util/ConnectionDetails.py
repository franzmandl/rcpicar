from __future__ import annotations
from typing import NamedTuple, Tuple


class ConnectionDetails(NamedTuple):
    own_address: Tuple[str, int]
    peer_address: Tuple[str, int]

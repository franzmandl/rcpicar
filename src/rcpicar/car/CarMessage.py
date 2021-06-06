from __future__ import annotations
from struct import pack, unpack
from typing import cast, Tuple
from ..message import IMessage

format_string = '<bb'
format_type = Tuple[int, int]


class CarMessage(IMessage):
    def __init__(self, speed: int, steering: int) -> None:
        self._speed = speed
        self._steering = steering

    def update(self, speed: int, steering: int) -> CarMessage:
        self._speed = speed
        self._steering = steering
        return self

    @property
    def speed(self) -> int:
        return self._speed

    @property
    def steering(self) -> int:
        return self._steering

    def encode(self) -> bytes:
        return pack(format_string, self._speed, self._steering)

    @staticmethod
    def decode(message: bytes) -> CarMessage:
        speed, steering = cast(format_type, unpack(format_string, message))
        return CarMessage(speed, steering)

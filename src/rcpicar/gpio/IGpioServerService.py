from abc import ABC, abstractmethod


class IGpioServerService(ABC):
    @abstractmethod
    def update(self, motor_value: int, steering_value: int) -> None:
        """"""

    @abstractmethod
    def reset(self) -> None:
        """"""

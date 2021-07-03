from abc import ABC, abstractmethod


class IGpio(ABC):
    @abstractmethod
    def set_mode(self, gpio: int, mode: int) -> None:
        """"""

    @abstractmethod
    def set_pwm_frequency(self, user_gpio: int, frequency: int) -> None:
        """"""

    @abstractmethod
    def set_pwm_range(self, user_gpio: int, range_: int) -> None:
        """"""

    @abstractmethod
    def set_pwm_duty_cycle(self, user_gpio: int, duty_cycle: int) -> None:
        """"""

    @abstractmethod
    def stop(self) -> None:
        """"""


class IGpioService(ABC):
    @abstractmethod
    def update(self, speed: int, steering: int) -> None:
        """"""

    def reset(self) -> None:
        self.update(0, 0)

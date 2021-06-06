from __future__ import annotations
from typing import Tuple
from rcpicar.gpio.IGpio import IGpio
from rcpicar.gpio.IGpioServerService import IGpioServerService
from tests.suite.spy import FunctionSpy


class MockGpio(IGpio):
    @staticmethod
    def create_dummy() -> MockGpio:
        mock = MockGpio()
        mock.set_mode_spy.constant(None)
        mock.set_pwm_frequency_spy.constant(None)
        mock.set_pwm_range_spy.constant(None)
        mock.set_pwm_duty_cycle_spy.constant(None)
        mock.stop_spy.constant(None)
        return mock

    def __init__(self) -> None:
        self.set_mode_spy: FunctionSpy[Tuple[int, int], None] = FunctionSpy()
        self.set_pwm_frequency_spy: FunctionSpy[Tuple[int, int], None] = FunctionSpy()
        self.set_pwm_range_spy: FunctionSpy[Tuple[int, int], None] = FunctionSpy()
        self.set_pwm_duty_cycle_spy: FunctionSpy[Tuple[int, int], None] = FunctionSpy()
        self.stop_spy: FunctionSpy[Tuple[()], None] = FunctionSpy()

    def set_mode(self, gpio: int, mode: int) -> None:
        self.set_mode_spy((gpio, mode))

    def set_pwm_frequency(self, user_gpio: int, frequency: int) -> None:
        self.set_pwm_frequency_spy((user_gpio, frequency))

    def set_pwm_range(self, user_gpio: int, range_: int) -> None:
        self.set_pwm_range_spy((user_gpio, range_))

    def set_pwm_duty_cycle(self, user_gpio: int, duty_cycle: int) -> None:
        self.set_pwm_duty_cycle_spy((user_gpio, duty_cycle))

    def stop(self) -> None:
        self.stop_spy(())


class MockGpioServerService(IGpioServerService):
    @staticmethod
    def create_dummy() -> MockGpioServerService:
        mock = MockGpioServerService()
        mock.update_spy.constant(None)
        mock.reset_spy.constant(None)
        return mock

    def __init__(self) -> None:
        self.update_spy: FunctionSpy[Tuple[int, int], None] = FunctionSpy()
        self.reset_spy: FunctionSpy[Tuple[()], None] = FunctionSpy()

    def update(self, motor_value: int, steering_value: int) -> None:
        self.update_spy((motor_value, steering_value))

    def reset(self) -> None:
        self.reset_spy(())

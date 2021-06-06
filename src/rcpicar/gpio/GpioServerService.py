from __future__ import annotations
from typing import Callable, Optional
from .IGpio import IGpio
from .IGpioServerService import IGpioServerService
from ..argument import IArguments
from ..service import AbstractService, AbstractServiceManager
from ..util.Placeholder import Placeholder
from ..util.util import min_max
from ..util.Lazy import Lazy


class GpioServerArguments(IArguments):
    def __init__(self) -> None:
        self.pwm_base = Lazy(lambda store: 300)
        self.pwm_frequency = Lazy(lambda store: 50)
        self.pwm_range = Lazy(lambda store: 4000)
        self.pwm_motor_base = Lazy(lambda store: self.pwm_base(store))
        self.pwm_motor_frequency = Lazy(lambda store: self.pwm_frequency(store))
        self.pwm_motor_gpio = Lazy(lambda store: 12)
        self.pwm_motor_invert = Lazy(lambda store: False)
        self.pwm_motor_maximum = Lazy(lambda store: 100)
        self.pwm_motor_minimum = Lazy(lambda store: -self.pwm_motor_maximum(store))
        self.pwm_motor_offset = Lazy(lambda store: 0)
        self.pwm_motor_range = Lazy(lambda store: self.pwm_range(store))
        self.pwm_steering_base = Lazy(lambda store: self.pwm_base(store))
        self.pwm_steering_frequency = Lazy(lambda store: self.pwm_frequency(store))
        self.pwm_steering_gpio = Lazy(lambda store: 13)
        self.pwm_steering_invert = Lazy(lambda store: False)
        self.pwm_steering_maximum = Lazy(lambda store: 100)
        self.pwm_steering_minimum = Lazy(lambda store: -self.pwm_steering_maximum(store))
        self.pwm_steering_offset = Lazy(lambda store: 0)
        self.pwm_steering_range = Lazy(lambda store: self.pwm_range(store))


class GpioServerService(IGpioServerService, AbstractService):
    def __init__(
            self, arguments: GpioServerArguments, gpio_factory: Callable[[], IGpio],
            service_manager: AbstractServiceManager,
    ) -> None:
        super().__init__(service_manager)
        self.arguments = arguments
        self.gpio_factory = gpio_factory
        self.gpio: Placeholder[IGpio] = Placeholder()

    def get_service_name(self) -> str:
        return __name__

    def join_service(self, timeout_seconds: Optional[float] = None) -> bool:
        return False

    def start_service(self) -> None:
        gpio = self.gpio_factory()
        gpio.set_mode(self.arguments.pwm_motor_gpio.get(), 1)
        gpio.set_pwm_frequency(self.arguments.pwm_motor_gpio.get(), self.arguments.pwm_motor_frequency.get())
        gpio.set_pwm_range(self.arguments.pwm_motor_gpio.get(), self.arguments.pwm_motor_range.get())
        _set_motor(self.arguments, gpio, 0)
        gpio.set_mode(self.arguments.pwm_steering_gpio.get(), 1)
        gpio.set_pwm_frequency(self.arguments.pwm_steering_gpio.get(), self.arguments.pwm_steering_frequency.get())
        gpio.set_pwm_range(self.arguments.pwm_steering_gpio.get(), self.arguments.pwm_steering_range.get())
        _set_steering(self.arguments, gpio, 0)
        self.gpio.set(gpio)

    def update(self, motor_value: int, steering_value: int) -> None:
        with self.gpio as (gpio, _):
            if gpio is not None:
                _set_motor(self.arguments, gpio, motor_value)
                _set_steering(self.arguments, gpio, steering_value)

    def reset(self) -> None:
        self.update(0, 0)

    def stop_service(self) -> None:
        self.reset()
        self.gpio.get_and_clear().stop()


def _set_motor(arguments: GpioServerArguments, gpio: IGpio, value: int) -> None:
    factor = -1 if arguments.pwm_motor_invert.get() else 1
    pwm_value = arguments.pwm_motor_base.get() + arguments.pwm_motor_offset.get() + min_max(
        value * factor, arguments.pwm_motor_minimum.get(), arguments.pwm_motor_maximum.get())
    gpio.set_pwm_duty_cycle(arguments.pwm_motor_gpio.get(), pwm_value)


def _set_steering(arguments: GpioServerArguments, gpio: IGpio, value: int) -> None:
    factor = -1 if arguments.pwm_steering_invert.get() else 1
    pwm_value = arguments.pwm_steering_base.get() + arguments.pwm_steering_offset.get() + min_max(
        value * factor, arguments.pwm_steering_minimum.get(), arguments.pwm_steering_maximum.get())
    gpio.set_pwm_duty_cycle(arguments.pwm_steering_gpio.get(), pwm_value)

from pigpio import pi
from .interfaces import IGpio


class PiGpio(IGpio):
    def __init__(self) -> None:
        self.pi = pi()

    def set_mode(self, gpio: int, mode: int) -> None:
        self.pi.set_mode(gpio, mode)

    def set_pwm_frequency(self, user_gpio: int, frequency: int) -> None:
        self.pi.set_PWM_frequency(user_gpio, frequency)

    def set_pwm_range(self, user_gpio: int, range_: int) -> None:
        self.pi.set_PWM_range(user_gpio, range_)

    def set_pwm_duty_cycle(self, user_gpio: int, duty_cycle: int) -> None:
        self.pi.set_PWM_dutycycle(user_gpio, duty_cycle)

    def stop(self) -> None:
        self.pi.stop()

class pi:
    def set_mode(self, gpio: int, mode: int) -> None:
        ...

    def set_PWM_frequency(self, user_gpio: int, frequency: int) -> None:
        ...

    def set_PWM_range(self, user_gpio: int, range_: int) -> None:
        ...

    def set_PWM_dutycycle(self, user_gpio: int, dutycycle: int) -> None:
        ...

    def stop(self) -> None:
        ...

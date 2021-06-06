from .Atomic import Atomic


class AtomicInteger(Atomic[int]):
    def __init__(self, value: int) -> None:
        super().__init__(value)

    def increment(self, amount: int = 1) -> None:
        with self as (value, set_value):
            set_value(value + amount)

from ..gpio.interfaces import IGpioService
from ..latency.interfaces import ILatencyListener
from ..latency.interfaces import ILatencyServerService
from ..timeout.interfaces import ITimeoutReceiveListener, ITimeoutReceiveService
from ..util.argument import IArguments
from ..util.Atomic import Atomic
from ..util.Lazy import Lazy
from ..util.util import min_max


class Throttle:
    def __init__(self, max_latency_seconds: float, max_speed: int) -> None:
        self.max_latency_seconds = max_latency_seconds
        self.max_speed = max_speed

    def get_throttled_speed(self, speed: int) -> int:
        return min_max(speed, -self.max_speed, self.max_speed)


class ThrottleServerArguments(IArguments):
    def __init__(self) -> None:
        self.throttle_upgrade_factor = Lazy(lambda store: 0.9)
        self.throttles = Lazy(lambda store: [Throttle(0.25, 100), Throttle(0.5, 50), Throttle(1.0, 10)])
        self.worst_throttle = Lazy(lambda store: Throttle(0.1, 0))


class ThrottleServerService(
    IGpioService,
    ILatencyListener,
    ITimeoutReceiveListener,
):
    def __init__(
            self,
            arguments: ThrottleServerArguments,
            gpio_service: IGpioService,
            latency_service: ILatencyServerService,
            timeout_service: ITimeoutReceiveService,
    ) -> None:
        self.arguments = arguments
        self.current_throttle = Atomic(arguments.worst_throttle.get())
        self.gpio_service = gpio_service
        self.timeout_service = timeout_service.add_timeout_listener(self)
        latency_service.add_latency_listener(self)

    def on_latency_available(self, latency: float) -> None:
        new_throttle = self.arguments.worst_throttle.get()
        for throttle in self.arguments.throttles.get():
            if latency <= throttle.max_latency_seconds:
                new_throttle = throttle
                break
        with self.current_throttle as (current_throttle, set_current_throttle):
            if new_throttle.max_latency_seconds < current_throttle.max_latency_seconds:
                if latency < new_throttle.max_latency_seconds * self.arguments.throttle_upgrade_factor.get():
                    set_current_throttle(new_throttle)
            else:
                set_current_throttle(new_throttle)
        self.timeout_service.set_timeout(new_throttle.max_latency_seconds)

    def on_latency_timeout(self) -> None:
        with self.current_throttle as (_, set_current_throttle):
            set_current_throttle(self.arguments.worst_throttle.get())

    def on_timeout_receive(self) -> None:
        self.gpio_service.reset()
        with self.current_throttle as (_, set_current_throttle):
            set_current_throttle(self.arguments.worst_throttle.get())

    def update(self, speed: int, steering: int) -> None:
        self.gpio_service.update(self.current_throttle.get().get_throttled_speed(speed), steering)

    def reset(self) -> None:
        self.gpio_service.reset()

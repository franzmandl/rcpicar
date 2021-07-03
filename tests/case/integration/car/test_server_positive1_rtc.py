from rcpicar.car.CarServerService import CarServerService
from rcpicar.expire.ExpireReceiveService import ExpireReceiveService
from rcpicar.message import message_types
from rcpicar.routed.RoutedReceiveService import RoutedReceiveService
from rcpicar.util.MultiServiceManager import MultiServiceManager
from rcpicar.priority.PriorityReceiveService import PriorityReceiveService
from rcpicar.throttle.ThrottleServerService import ThrottleServerArguments, ThrottleServerService
from rcpicar.timeout.TimeoutReceiveService import TimeoutReceiveService
from rcpicar.util.RTC import rtc
from tests.mock.gpio import MockGpioService
from tests.mock.helper import create_car_message, mock_seconds
from tests.mock.latency import MockLatencyServerService
from tests.mock.receive import MockReceiveService
from tests.mock.reliable import MockReliableService


def test() -> None:
    # given
    mock_gpio = MockGpioService.create_dummy()
    mock_latency = MockLatencyServerService.create_dummy()
    mock_receive = MockReceiveService.Tunnel()
    mock_reliable = MockReliableService.create_dummy()
    service_manager = MultiServiceManager()
    car_receive_service = RoutedReceiveService(mock_receive.mock).create_receive_service(message_types.car)
    priority_service = PriorityReceiveService(rtc, car_receive_service, service_manager, mock_seconds)
    expire_service = ExpireReceiveService(priority_service)
    timeout_service = TimeoutReceiveService(rtc, expire_service, service_manager)
    throttle_service = ThrottleServerService(ThrottleServerArguments(), mock_gpio, mock_latency, timeout_service)
    CarServerService(expire_service, throttle_service, mock_reliable, timeout_service)
    # when
    with rtc.use_services(service_manager):
        throttle_service.on_latency_available(0.1)
        mock_receive.send(create_car_message(10, 20).expire(1).priority(128).routed().encode())
    # then
    assert mock_gpio.update_spy.get_called_args() == [(10, 20)]


if __name__ == '__main__':
    test()

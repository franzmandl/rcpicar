from rcpicar.car.CarServerService import CarServerArguments, CarServerService
from rcpicar.routed.RoutedReceiveService import RoutedReceiveService
from rcpicar.util.MultiServiceManager import MultiServiceManager
from rcpicar.util.RTC import rtc
from tests.mock.gpio import MockGpioServerService
from tests.mock.helper import create_car_message
from tests.mock.latency import MockLatencyServerService
from tests.mock.receive import MockReceiveService
from tests.mock.reliable import MockReliableService


def test() -> None:
    # given
    mock_gpio = MockGpioServerService.create_dummy()
    mock_latency = MockLatencyServerService.create_dummy()
    mock_receive = MockReceiveService.Tunnel()
    mock_reliable = MockReliableService.create_dummy()
    service_manager = MultiServiceManager(rtc)
    car_service = CarServerService(
        CarServerArguments(), rtc, mock_gpio, mock_latency, mock_reliable, RoutedReceiveService(mock_receive.mock),
        service_manager)
    car_service.throttle_service.on_latency_available(0.1)
    # when
    with service_manager:
        mock_receive.send(create_car_message(10, 20).expire(1).priority(128).routed().encode())
    # then
    assert mock_gpio.update_spy.get_called_args() == [(10, 20)]


if __name__ == '__main__':
    test()

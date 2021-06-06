from rcpicar.car.CarClientService import CarClientArguments, CarClientService
from rcpicar.routed.RoutedSendService import RoutedSendService
from rcpicar.util.MultiServiceManager import MultiServiceManager
from rcpicar.util.RTC import rtc
from tests.mock.helper import create_car_message
from tests.mock.reliable import MockReliableService
from tests.mock.send import MockSendService


def test() -> None:
    # given
    mock_send = MockSendService.create_dummy()
    mock_reliable = MockReliableService.create_dummy()
    service_manager = MultiServiceManager(rtc)
    service = CarClientService(CarClientArguments(), rtc, mock_reliable, RoutedSendService(mock_send), service_manager)
    # when
    with service_manager:
        service.update(10, 20)
    # then
    assert mock_send.send_spy.get_called_args() == [
        (create_car_message(10, 20).expire(1).priority(128).routed().encode(),)]


if __name__ == '__main__':
    test()

from rcpicar.car.CarClientService import CarClientService
from rcpicar.expire.ExpireSendService import ExpireSendService
from rcpicar.message import message_types
from rcpicar.priority.PrioritySendService import PrioritySendService
from rcpicar.routed.RoutedSendService import RoutedSendService
from rcpicar.util.MultiServiceManager import MultiServiceManager
from rcpicar.util.RTC import rtc
from rcpicar.timeout.TimeoutSendService import TimeoutSendService
from tests.mock.helper import create_car_message, mock_seconds
from tests.mock.reliable import MockReliableService
from tests.mock.send import MockSendService


def test() -> None:
    # given
    mock_send = MockSendService.create_dummy()
    mock_reliable = MockReliableService.create_dummy()
    service_manager = MultiServiceManager()
    car_send_service = RoutedSendService(mock_send).create_send_service(message_types.car)
    priority_service = PrioritySendService(128, car_send_service)
    expire_service = ExpireSendService(priority_service)
    timeout_service = TimeoutSendService(rtc, expire_service, service_manager, mock_seconds)
    service = CarClientService(mock_reliable, timeout_service)
    # when
    with rtc.use_services(service_manager):
        service.update(10, 20)
    # then
    assert mock_send.send_spy.get_called_args() == [
        (create_car_message(10, 20).expire(1).priority(128).routed().encode(),)]


if __name__ == '__main__':
    test()

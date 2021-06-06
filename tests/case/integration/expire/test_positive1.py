from rcpicar.expire.ExpireMessage import ExpireMessage, valid_message_number_range
from rcpicar.expire.ExpireReceiveService import ExpireReceiveService
from tests.mock.receive import MockReceiveService


def test() -> None:
    mock_receive = MockReceiveService.Tunnel()
    service = ExpireReceiveService(mock_receive.mock)
    assert service.last_message_number._value == 0
    mock_receive.send(ExpireMessage(12, b'').encode())
    assert service.last_message_number._value == 12
    mock_receive.send(ExpireMessage(9, b'').encode())
    assert service.last_message_number._value == 12
    mock_receive.send(ExpireMessage(25, b'').encode())
    assert service.last_message_number._value == 25
    mock_receive.send(ExpireMessage(25 + valid_message_number_range, b'').encode())
    assert service.last_message_number._value == 25
    mock_receive.send(ExpireMessage(25 + valid_message_number_range - 1, b'').encode())
    assert service.last_message_number._value == 16408


if __name__ == '__main__':
    test()

from rcpicar.expire.ExpireMessage import ExpireMessage, valid_message_number_range
from rcpicar.expire.ExpireReceiveService import ExpireReceiveService
from tests.mock.receive import MockReceiveService


def test() -> None:
    mock_receive = MockReceiveService.Tunnel()
    service = ExpireReceiveService(mock_receive.mock)
    assert service.last_message_number._value == 0
    for i in range(4):
        mock_receive.send(ExpireMessage((valid_message_number_range - 1) * (i + 1), b'').encode())
        assert service.last_message_number._value == 16383 * (i + 1)
    assert service.last_message_number._value == 65532
    mock_receive.send(ExpireMessage(16380, b'').encode())
    assert service.last_message_number._value == 65532
    mock_receive.send(ExpireMessage(16379, b'').encode())
    assert service.last_message_number._value == 16379


if __name__ == '__main__':
    test()

from subprocess import PIPE
from rcpicar.constants import caps_line_prefix
from rcpicar.gstreamer.GStreamerServerService import GStreamerServerArguments, GStreamerServerService
from rcpicar.routed.RoutedReceiveService import RoutedReceiveService
from rcpicar.routed.RoutedSendService import RoutedSendService
from rcpicar.util.MultiServiceManager import MultiServiceManager
from rcpicar.util.RTC import rtc
from tests.mock.helper import create_video_request_message, create_video_response_message, mock_client_address
from tests.mock.helper import mock_video_settings
from tests.mock.process import MockIO, MockProcess, MockProcessFactory
from tests.mock.receive import MockReceiveService
from tests.mock.reliable import MockReliableService
from tests.mock.send import MockSendService


def test() -> None:
    # given
    mock_caps = '~~CAPS~~'
    mock_receive = MockReceiveService.Tunnel()
    mock_send = MockSendService.create_dummy()
    mock_reliable = MockReliableService.create_dummy()
    mock_gst_launch_output = MockIO()
    mock_gst_launch_output.readline_spy.iterable([
        b'a\n', b'b\n', b'c\n', f'{caps_line_prefix}{mock_caps}\n'.encode(), b'd\n', b'e\n'])
    mock_gst_launch_process = MockProcess.create_dummy()
    mock_gst_launch_process.get_stdout_spy.constant(mock_gst_launch_output)
    mock_raspivid_output = MockIO()
    mock_raspivid_process = MockProcess.create_dummy()
    mock_raspivid_process.get_stdout_spy.constant(mock_raspivid_output)
    mock_process_factory = MockProcessFactory()
    mock_process_factory.call___spy.mapping({
        ((
            'gst-launch-1.0', '-v', 'fdsrc', '!', 'h264parse', '!', 'rtph264pay', '!', 'udpsink',
            f'host={mock_client_address[0]}', f'port={mock_client_address[1]}'), mock_raspivid_output, PIPE):
                mock_gst_launch_process,
        ((
            'raspivid', '-n', '-t', '0', '-h', str(mock_video_settings.height), '-w', str(mock_video_settings.width),
            '-fps', str(mock_video_settings.fps), '-b', str(mock_video_settings.bit_rate), '-o', '-'), None, PIPE):
                mock_raspivid_process,
    })
    service_manager = MultiServiceManager(rtc)
    GStreamerServerService(
        GStreamerServerArguments(), mock_process_factory, RoutedReceiveService(mock_receive.mock), mock_reliable,
        RoutedSendService(mock_send), service_manager)
    # when
    with service_manager:
        mock_receive.send(create_video_request_message(mock_client_address, mock_video_settings).routed().encode())
    # then
    assert mock_process_factory.call___spy.get_times_called() == 2
    assert mock_send.send_spy.get_called_args() == [
        (create_video_response_message(mock_caps, mock_client_address[1]).routed().encode(),)]
    assert mock_raspivid_process.terminate_spy.get_called_args() == [()]


if __name__ == '__main__':
    test()

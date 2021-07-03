from subprocess import PIPE
from rcpicar.constants import caps_line_prefix
from rcpicar.gstreamer.GStreamerServerService import GStreamerServerArguments, GStreamerServerService
from rcpicar.message import message_types
from rcpicar.routed.RoutedReceiveService import RoutedReceiveService
from rcpicar.routed.RoutedSendService import RoutedSendService
from rcpicar.util.MultiServiceManager import MultiServiceManager
from rcpicar.util.RTC import rtc
from tests.mock.helper import create_gstreamer_request_message, create_gstreamer_response_message, mock_client_address
from tests.mock.helper import mock_video_settings
from tests.mock.process import MockIO, MockProcess, MockProcessFactory
from tests.mock.receive import MockReceiveService
from tests.mock.reliable import MockReliableService
from tests.mock.send import MockSendService


def test() -> None:
    # given
    another_client_address = ('client2', 7851)
    mock_caps = '~~CAPS~~'
    mock_receive = MockReceiveService.Tunnel()
    mock_send = MockSendService.create_dummy()
    mock_reliable = MockReliableService.create_dummy()
    mock_gst_launch_output_iterable = [
        b'a\n', b'b\n', b'c\n', f'{caps_line_prefix}{mock_caps}\n'.encode(), b'd\n', b'e\n']
    mock_gst_launch_output1 = MockIO()
    mock_gst_launch_output1.readline_spy.iterable(mock_gst_launch_output_iterable)
    mock_gst_launch_process1 = MockProcess.create_dummy()
    mock_gst_launch_process1.get_stdout_spy.constant(mock_gst_launch_output1)
    mock_gst_launch_output2 = MockIO()
    mock_gst_launch_output2.readline_spy.iterable(mock_gst_launch_output_iterable)
    mock_gst_launch_process2 = MockProcess.create_dummy()
    mock_gst_launch_process2.get_stdout_spy.constant(mock_gst_launch_output2)
    mock_raspivid_output = MockIO()
    mock_raspivid_process = MockProcess.create_dummy()
    mock_raspivid_process.get_stdout_spy.constant(mock_raspivid_output)
    mock_process_factory = MockProcessFactory()
    mock_process_factory.call___spy.mapping({
        ((
            'gst-launch-1.0', '-v', 'fdsrc', '!', 'h264parse', '!', 'rtph264pay', '!', 'udpsink',
            f'host={mock_client_address[0]}', f'port={mock_client_address[1]}'), mock_raspivid_output, PIPE):
                mock_gst_launch_process1,
        ((
            'gst-launch-1.0', '-v', 'fdsrc', '!', 'h264parse', '!', 'rtph264pay', '!', 'udpsink',
            f'host={another_client_address[0]}', f'port={another_client_address[1]}'), mock_raspivid_output, PIPE):
                mock_gst_launch_process2,
        ((
            'raspivid', '-n', '-t', '0', '-h', str(mock_video_settings.height), '-w', str(mock_video_settings.width),
            '-fps', str(mock_video_settings.fps), '-b', str(mock_video_settings.bit_rate), '-o', '-'), None, PIPE):
                mock_raspivid_process,
    })
    service_manager = MultiServiceManager()
    GStreamerServerService(
        GStreamerServerArguments(), mock_process_factory,
        RoutedReceiveService(mock_receive.mock).create_receive_service(message_types.gstreamer), mock_reliable,
        RoutedSendService(mock_send).create_send_service(message_types.gstreamer), service_manager)
    # when
    with rtc.use_services(service_manager):
        mock_receive.send(create_gstreamer_request_message(mock_client_address, mock_video_settings).routed().encode())
        mock_receive.send(create_gstreamer_request_message(
            another_client_address, mock_video_settings).routed().encode())
    # then
    assert mock_process_factory.call___spy.get_times_called() == 4
    assert mock_send.send_spy.get_called_args() == [
        (create_gstreamer_response_message(mock_caps, mock_client_address[1]).routed().encode(),),
        (create_gstreamer_response_message(mock_caps, another_client_address[1]).routed().encode(),),
    ]
    assert mock_raspivid_process.terminate_spy.get_called_args() == [(), ()]


if __name__ == '__main__':
    test()

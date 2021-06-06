from rcpicar.message import message_types
from rcpicar.throttle.ThrottleServerService import Throttle
from rcpicar.util.RTC import rtc
from tests.mock.helper import create_car_message, mock_client_address
from tests.case.system.ctx import Context, ServerContext


def test() -> None:
    # given
    ctx = Context(rtc)
    server_ctx = ServerContext(ctx)
    throttle = Throttle(1000.0, 55)
    server_ctx.server.car_arguments.throttle.throttles.set([throttle])
    server_ctx.server.car_service.get()
    server_ctx.server.discovery_service.get()
    server_ctx.server.gstreamer_service.get()
    server_ctx.server.latency_service.get()
    worst_throttle = server_ctx.server.car_arguments.throttle.worst_throttle.get()
    # when
    with server_ctx.server.service_manager.get():
        server_ctx.gpio.set_pwm_duty_cycle_spy.wait_for_calls(2)
        assert server_ctx.gpio.set_pwm_duty_cycle_spy.consume_called_args() == [(12, 300), (13, 300)]
        ctx.udp_client_to_server_queue.put(
            create_car_message(10, 20).expire(1).priority(128).routed().udp_tuple(False))
        # No throttle set yet because we did not respond the latency message yet
        assert server_ctx.server.car_service.get().throttle_service.current_throttle.get() == worst_throttle
        server_ctx.gpio.set_pwm_duty_cycle_spy.wait_for_calls(2)
        assert server_ctx.gpio.set_pwm_duty_cycle_spy.consume_called_args() == [(12, 300), (13, 320)]
        # Echo latest latency message
        encoded_routed_latency_message, _ = ctx.udp_server_to_client_queue.get()
        assert ctx.udp_server_to_client_queue.empty()
        assert encoded_routed_latency_message[0] == message_types.latency
        ctx.udp_client_to_server_queue.put((encoded_routed_latency_message, mock_client_address))
        # Throttle has been set
        ctx.udp_client_to_server_queue.join()
        server_ctx.server.latency_service.get().received_messages.join()
        assert server_ctx.server.car_service.get().throttle_service.current_throttle.get() == throttle
        ctx.udp_client_to_server_queue.put(
            create_car_message(80, 60).expire(2).priority(128).routed().udp_tuple(False))
        ctx.udp_client_to_server_queue.join()
    # then
    assert server_ctx.gpio.set_pwm_duty_cycle_spy.consume_called_args() == [
        (12, 355), (13, 360),
        # Shutting down
        (12, 300), (13, 300),
    ]


if __name__ == '__main__':
    test()

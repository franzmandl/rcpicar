from rcpicar.util.RTC import rtc
from tests.mock.helper import create_car_message, mock_seconds
from tests.case.system.ctx import Context, ServerContext


def test() -> None:
    # given
    ctx = Context(rtc)
    server_ctx = ServerContext(ctx)
    # Bypass throttle
    server_ctx.server.throttle_service.set(server_ctx.server.gpio_service.get())
    server_ctx.server.timeout_service.get().set_timeout(mock_seconds)
    server_ctx.server.car_service.get()
    server_ctx.server.discovery_service.get()
    server_ctx.server.gstreamer_service.get()
    # when
    with rtc.use_services(server_ctx.server.service_manager.get()):
        server_ctx.gpio.set_pwm_duty_cycle_spy.wait_for_calls(2)
        assert server_ctx.gpio.set_pwm_duty_cycle_spy.consume_called_args() == [(12, 300), (13, 300)]
        ctx.udp_client_to_server_queue.put(
            create_car_message(10, 20).expire(1).priority(128).routed().udp_tuple(False))
        server_ctx.gpio.set_pwm_duty_cycle_spy.wait_for_calls(2)
        assert server_ctx.gpio.set_pwm_duty_cycle_spy.consume_called_args() == [(12, 310), (13, 320)]
        ctx.udp_client_to_server_queue.join()
        server_ctx.latency_service.received_messages.join()
        ctx.udp_client_to_server_queue.put(
            create_car_message(80, 60).expire(2).priority(128).routed().udp_tuple(False))
        ctx.udp_client_to_server_queue.join()
    # then
    assert server_ctx.gpio.set_pwm_duty_cycle_spy.consume_called_args() == [
        (12, 380), (13, 360),
        # Shutting down
        (12, 300), (13, 300),
    ]


if __name__ == '__main__':
    test()

from tests.mock.clock import MockClock
from tests.mock.helper import create_car_message, create_latency_message, mock_client_address
from tests.case.system.ctx import Context, ServerContext


def test() -> None:
    # given
    mock_clock = MockClock()
    ctx = Context(mock_clock)
    server_ctx = ServerContext(ctx)
    server_ctx.server.clock.set(mock_clock)
    server_ctx.server.car_service.get()
    server_ctx.server.discovery_service.get()
    server_ctx.server.gstreamer_service.get()
    server_ctx.server.latency_service.get()
    throttles = server_ctx.server.throttle_arguments.throttles.get()
    worst_throttle = server_ctx.server.throttle_arguments.worst_throttle.get()
    # when
    with server_ctx.server.use_services():
        assert server_ctx.gpio.set_pwm_duty_cycle_spy.consume_called_args() == [(12, 300), (13, 300)]
        mock_clock.sleep_till(
            lambda: server_ctx.latency_service.received_messages in mock_clock.waiting_queues)
        mock_clock.tick(9)
        ctx.udp_client_to_server_queue.put(
            create_car_message(10, 20).expire(1).priority(128).routed().udp_tuple(False))
        # No throttle set yet because we did not respond the latency message yet
        assert server_ctx.throttle_service.current_throttle.get() == worst_throttle
        mock_clock.notify_till(
            lambda: server_ctx.gpio.set_pwm_duty_cycle_spy.consume_called_args() == [(12, 300), (13, 320)])
        # Echo second (=latest) latency message
        mock_clock.tick()
        mock_clock.notify_till(lambda: not ctx.udp_server_to_client_queue.empty())
        encoded_routed_latency_message, _ = ctx.udp_server_to_client_queue.get()
        assert ctx.udp_server_to_client_queue.empty()
        assert encoded_routed_latency_message == create_latency_message(2).routed().encode()
        ctx.udp_client_to_server_queue.put((encoded_routed_latency_message, mock_client_address))
        # Throttle has been set
        mock_clock.notify_till(lambda: ctx.udp_client_to_server_queue.empty())
        mock_clock.notify_till(lambda: server_ctx.latency_service.received_messages.empty())
        assert server_ctx.throttle_service.current_throttle.get() == throttles[0]
        ctx.udp_client_to_server_queue.put(
            create_car_message(80, 60).expire(2).priority(128).routed().udp_tuple(False))
        mock_clock.notify_till(lambda: ctx.udp_client_to_server_queue.empty())
    # then
    assert server_ctx.gpio.set_pwm_duty_cycle_spy.consume_called_args() == [
        (12, 380), (13, 360),
        # Shutting down
        (12, 300), (13, 300),
    ]


if __name__ == '__main__':
    test()

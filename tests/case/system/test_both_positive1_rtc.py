from time import sleep
from rcpicar.util.RTC import rtc
from tests.case.system.ctx import Context, ClientContext, ServerContext


def test() -> None:
    # given
    ctx = Context(rtc)
    client_ctx = ClientContext(ctx)
    server_ctx = ServerContext(ctx)
    client_ctx.client.car_service.get()
    server_ctx.server.car_service.get()
    client_ctx.client.discovery_service.get()
    server_ctx.server.discovery_service.get()
    client_ctx.client.gstreamer_service.get()
    server_ctx.server.gstreamer_service.get()
    client_ctx.client.latency_service.get()
    server_ctx.server.latency_service.get()
    # when
    with server_ctx.server.use_services():
        with client_ctx.client.use_services():
            sleep(2)
    # then
    assert server_ctx.gpio.set_pwm_frequency_spy.get_called_args() == [(12, 50), (13, 50)]
    assert server_ctx.gpio.set_pwm_range_spy.get_called_args() == [(12, 4000), (13, 4000)]
    assert server_ctx.gpio.set_mode_spy.get_called_args() == [(12, 1), (13, 1)]
    set_pwm_duty_cycle_args = server_ctx.gpio.set_pwm_duty_cycle_spy.get_called_args()
    assert len(set_pwm_duty_cycle_args) > 0 and len(set_pwm_duty_cycle_args) % 2 == 0
    assert set_pwm_duty_cycle_args == [(12 + index % 2, 300) for index in range(len(set_pwm_duty_cycle_args))]
    assert server_ctx.gpio.stop_spy.get_called_args() == [()]


if __name__ == '__main__':
    test()

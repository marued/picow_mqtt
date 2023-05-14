from machine import Pin, Timer


class HepticMotor:
    def __init__(self, pinNumber: int) -> None:
        self.pin = Pin(pinNumber, Pin.OUT)
        self.timer = Timer()

    def activate(self, ms: int = 500) -> None:
        self.pin.high()
        lambda_stop = lambda t: self.pin.low()
        self.timer.init(mode=Timer.ONE_SHOT, period=ms, callback=lambda_stop)

    def deactivate(self) -> None:
        self.pin.low()
        self.timer.deinit()

    # set interval for a limited period of time
    def activate_limited_interval(self, period: int, duration: int) -> None:
        self.timer.init(
            mode=Timer.PERIODIC, period=period, callback=lambda t: self.pin.toggle()
        )
        lambda_stop = lambda t: self.deactivate()
        self.timer.init(mode=Timer.ONE_SHOT, period=duration, callback=lambda_stop)

    def activate_interval(self, ms: int) -> None:
        self.timer.init(
            mode=Timer.PERIODIC, period=ms, callback=lambda t: self.pin.toggle()
        )


if __name__ == "__main__":
    print("Executing heptic motor main")
    motor = HepticMotor(2)
    motor.activate()

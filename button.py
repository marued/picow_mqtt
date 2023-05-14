from machine import Pin
import time
import uasyncio


class Button:
    """
    class description:
        This class is used to register callbacks for button press, double press and long press.
        It uses the irq of the button pin to register the callbacks.
        To avoid multiple callbacks to be executed at the same time it uses a thread safe flag
        from uasyncio. The callbacks in `start_listening` are executed in a subtask and not in
        the irq.

    Code example:
        button = Button(17, 2)
        button.start_listening(
            single_press_callback,
            double_press_callback,
            long_press_callback,
            single_press_interval=500,
            double_press_interval=500,
            long_press_interval=1000,
        )
    """

    def __init__(self, buttonPin: int, hepticPin: int) -> None:
        self.pin = Pin(buttonPin, mode=Pin.IN, pull=Pin.PULL_DOWN)
        self.heptinc_motor = Pin(hepticPin, mode=Pin.OUT)
        self.button_thread_safe_flag = uasyncio.ThreadSafeFlag()

    def start_listening(
        self,
        single_press_callback,
        double_press_callback,
        long_press_callback,
        single_press_interval=500,
        double_press_interval=500,
        long_press_interval=1000,
    ):
        self.single_press_callback = single_press_callback
        self.double_press_callback = double_press_callback
        self.long_press_callback = long_press_callback
        self.single_press_interval = single_press_interval
        self.double_press_interval = double_press_interval
        self.long_press_interval = long_press_interval

        self.listen_to_button_change(self._register_button_change_irq)
        uasyncio.create_task(self._listen_button_pressed())

    def is_pressed(self) -> bool:
        return self.pin.value() == 1

    def listen_to_button_press(self, callback):
        self.pin.irq(trigger=Pin.IRQ_RISING, handler=callback, hard=True)

    def listen_to_button_release(self, callback) -> None:
        self.pin.irq(trigger=Pin.IRQ_FALLING, handler=callback, hard=True)

    def listen_to_button_change(self, callback) -> None:
        self.pin.irq(
            trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=callback, hard=True
        )

    def _register_button_change_irq(self, pin: Pin) -> None:
        if pin.value() == 1:
            print("button pressed")
            self.heptinc_motor.high()
            self.button_thread_safe_flag.set()
        else:
            print("button released")
            self.heptinc_motor.low()

    async def _listen_button_pressed(self) -> None:
        while True:
            await self.button_thread_safe_flag.wait()
            await self._on_button_pressed()
            await uasyncio.sleep_ms(100)

    async def _on_button_pressed(self) -> None:
        start_time = time.ticks_ms()
        while self.is_pressed():
            # keeped pressed for the given interval
            if start_time + self.long_press_interval < time.ticks_ms():
                print("long press")
                self.long_press_callback(self.pin)
                self.button_thread_safe_flag.clear()
                return
            # sleep for 10ms to avoid busy waiting
            await uasyncio.sleep_ms(50)

        start_time = time.ticks_ms()
        while not self.is_pressed():
            # Did not press for the given interval
            if start_time + self.double_press_interval < time.ticks_ms():
                print("single press")
                self.single_press_callback(self.pin)
                self.button_thread_safe_flag.clear()
                return
            # sleep for 10ms to avoid busy waiting
            await uasyncio.sleep_ms(50)

        print("double press")
        self.double_press_callback(self.pin)
        self.button_thread_safe_flag.clear()

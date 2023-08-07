from machine import Pin
import time
import uasyncio
import machine


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
        self.button_pressed_counter = 0

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

        # IRQ does not work with uasyncio
        self.listen_to_button_change(self._register_button_change_irq)
        return self._listen_button_pressed()

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
            print("heptic motor on")
            # self.button_thread_safe_flag.set()
            self.heptinc_motor.high()
        else:
            print("heptic motor off")
            self.heptinc_motor.low()

    async def _listen_button_pressed(self) -> None:
        try:
            while True:
                if self.is_pressed() and self.button_pressed_counter == 0:
                    print("button pressed")
                    self.button_pressed_counter += 1
                    await self._on_button_pressed()
                elif not self.is_pressed() and self.button_pressed_counter > 0:
                    self.button_pressed_counter = 0
                await uasyncio.sleep_ms(20)

        except Exception as e:
            print("Error on listen button pressed: {0}".format(e))

    async def _on_button_pressed(self) -> None:
        start_time = time.ticks_ms()
        try:
            while self.is_pressed():
                # keeped pressed for the given interval
                if start_time + self.long_press_interval < time.ticks_ms():
                    print("long press")
                    await self.long_press_callback(self.pin)
                    return
                # sleep for 10ms to avoid busy waiting
                await uasyncio.sleep_ms(10)

            start_time = time.ticks_ms()
            while not self.is_pressed():
                # Did not press for the given interval
                if start_time + self.double_press_interval < time.ticks_ms():
                    print("single press")
                    await self.single_press_callback(self.pin)
                    return
                # sleep for 10ms to avoid busy waiting
                await uasyncio.sleep_ms(10)

            print("double press")
            await self.double_press_callback(self.pin)

        except Exception as e:
            print("Error on button pressed: {0}".format(e))

from machine import Pin, Timer
from cofee_table.ir_tx.nec import NEC


# Class that activates the IR diode linked to the GPIO pin
class SamsungIRTransmitter:
    # map definition of the adress and data with button name as string
    actions = {
        "power": {"addr": 0x0707, "data": 0x02},
        "volume_up": {"addr": 0x0707, "data": 0x07},
        "volume_down": {"addr": 0x0707, "data": 0x0B},
        "channel_up": {"addr": 0x0707, "data": 0x12},
        "channel_down": {"addr": 0x0707, "data": 0x10},
        "mute": {"addr": 0x0707, "data": 0x0F},
        "source": {"addr": 0x0707, "data": 0x01},
    }

    def __init__(self, pinNumber: int) -> None:
        self.transmitter = NEC(Pin(pinNumber))
        self.transmitter.samsung = True
        self.timer = Timer()

    def activate(self, action: str) -> None:
        print("Activating action: " + action)
        self.transmitter.transmit(
            data=self.actions[action]["data"], addr=self.actions[action]["addr"]
        )

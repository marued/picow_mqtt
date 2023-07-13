from machine import Pin, Timer
from cofee_table.ir_tx.nec import NEC


# Class that activates the IR diode linked to the GPIO pin
class SamsungIRTransmitter:
    # map definition of the adress and data with button name as string
    actions = {
        "tv_power": {"addr": 0x0707, "data": 0x02},
        "tv_volume_up": {"addr": 0x0707, "data": 0x07},
        "tv_volume_down": {"addr": 0x0707, "data": 0x0B},
        "tv_channel_up": {"addr": 0x0707, "data": 0x12},
        "tv_channel_down": {"addr": 0x0707, "data": 0x10},
        "tv_mute": {"addr": 0x0707, "data": 0x0F},
        "tv_source": {"addr": 0x0707, "data": 0x01},
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

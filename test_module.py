from utime import sleep_ms
import machine
import uasyncio
from cofee_table.button import Button
from cofee_table.heptic_motor import HepticMotor
from cofee_table.mqtt import MQTT
from cofee_table.samsung_ir_transmitter import SamsungIRTransmitter


class TableModule:
    def __init__(self):
        self.button_1 = Button(17, 2)
        self.samsung_ir_transmitter = SamsungIRTransmitter(15)
        self.mqtt_server = MQTT()

    def connect(self):
        self.mqtt_server.connect()
        self.mqtt_server.mqtt_connect()

    def register_callbacks(self):
        self.button_1.start_listening(
            self.single_click_callback,
            self.double_click_callback,
            self.long_click_callback,
        )
        self.mqtt_server.register_callback(
            b"power", lambda topic, msg: self.samsung_ir_transmitter.activate("volume_up")
        )
        self.mqtt_server.register_callback(
            b"source", lambda topic, msg: self.samsung_ir_transmitter.activate("source")
        )

    def single_click_callback(self, pin: machine.Pin):
        print("single click")
        self.mqtt_server.publish(topic_msg=b"single click")

    def double_click_callback(self, pin: machine.Pin):
        print("double click")
        self.mqtt_server.publish(topic_msg=b"double click")
        self.samsung_ir_transmitter.activate("power")

    def long_click_callback(self, pin: machine.Pin):
        print("long click")
        self.mqtt_server.publish(topic_msg=b"long click")
        self.samsung_ir_transmitter.activate("source")


async def start():
    print("Executing main")
    table_module = TableModule()
    table_module.connect()
    table_module.register_callbacks()
    table_module.mqtt_server.start_msg_check()
    while True:
        await uasyncio.sleep(100)


if __name__ == "__main__":
    # Need to run subrutine so it can yield to
    # others and not exit the main thread
    uasyncio.run(start())
    

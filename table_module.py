import machine
from cofee_table.button import Button
from cofee_table.mqtt import MQTT
from cofee_table.samsung_ir_transmitter import SamsungIRTransmitter
import cofee_table.config as config


class TableModule:
    def __init__(self, buttons: list, ir_transmitter_pin_nb: int = 15):
        self.buttons = []
        self.buttons_metadata = buttons
        for button in buttons:
            self.buttons.append(Button(button["pin_nb"], button["heptic_pin_nb"]))
        self.samsung_ir_transmitter = SamsungIRTransmitter(ir_transmitter_pin_nb)
        self.mqtt_server = MQTT()

    def connect(self):
        self.mqtt_server.connect(config.ssid, config.password)
        self.mqtt_server.mqtt_connect(
            config.mqtt_server,
            config.mqtt_port,
            config.client_username,
            config.client_psw,
            config.client_id,
        )

    def register_callbacks(self):
        index = 0
        for button in self.buttons:
            button.start_listening(
                self.single_click_callback(self.buttons_metadata[index]),
                self.double_click_callback(self.buttons_metadata[index]),
                self.long_click_callback(self.buttons_metadata[index]),
            )
            index += 1

        self.mqtt_server.register_callback(
            b"power",
            lambda topic, msg: self.samsung_ir_transmitter.activate("power"),
        )
        self.mqtt_server.register_callback(
            b"source", lambda topic, msg: self.samsung_ir_transmitter.activate("source")
        )
        self.mqtt_server.register_callback(
            b"volume_up",
            lambda topic, msg: self.samsung_ir_transmitter.activate("volume_up"),
        )
        self.mqtt_server.register_callback(
            b"volume_down",
            lambda topic, msg: self.samsung_ir_transmitter.activate("volume_down"),
        )

    def single_click_callback(self, button_metadata: dict) -> function:
        def execute(pin: machine.Pin):
            print("single click")
            self.mqtt_server.publish(
                topic_msg="single click {0}".format(button_metadata["pin_nb"]).encode(
                    "utf-8"
                )
            )
            if "single_click_action" in button_metadata:
                self.samsung_ir_transmitter.activate(
                    button_metadata["single_click_action"]
                )

        return execute

    def double_click_callback(self, button_metadata: dict):
        def execute(pin: machine.Pin):
            print("double click")
            self.mqtt_server.publish(
                topic_msg="double click {0}".format(button_metadata["pin_nb"]).encode(
                    "utf-8"
                )
            )
            if "double_click_action" in button_metadata:
                self.samsung_ir_transmitter.activate(
                    button_metadata["double_click_action"]
                )

        return execute
        # self.samsung_ir_transmitter.activate("power")

    def long_click_callback(self, button_metadata: dict):
        def execute(pin: machine.Pin):
            print("long click")
            self.mqtt_server.publish(
                topic_msg="long click {0}".format(button_metadata["pin_nb"]).encode(
                    "utf-8"
                )
            )
            if "long_click_action" in button_metadata:
                self.samsung_ir_transmitter.activate(
                    button_metadata["long_click_action"]
                )

        return execute
        # self.samsung_ir_transmitter.activate("source")

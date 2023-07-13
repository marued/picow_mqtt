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

        # Register MQTT callbacks for TV commands
        self.mqtt_server.register_callback(
            b"tv_power",
            lambda topic, msg: self.samsung_ir_transmitter.activate("tv_power"),
        )
        self.mqtt_server.register_callback(
            b"tv_source",
            lambda topic, msg: self.samsung_ir_transmitter.activate("tv_source"),
        )
        self.mqtt_server.register_callback(
            b"tv_volume_up",
            lambda topic, msg: self.samsung_ir_transmitter.activate("tv_volume_up"),
        )
        self.mqtt_server.register_callback(
            b"tv_volume_down",
            lambda topic, msg: self.samsung_ir_transmitter.activate("tv_volume_down"),
        )

    def single_click_callback(self, button_metadata: dict) -> function:
        def execute(pin: machine.Pin):
            print("single click")
            self.mqtt_server.publish(
                topic_msg=b"single click",
                topic_pub=self._get_topic(button_metadata),
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
                topic_msg=b"double click",
                topic_pub=self._get_topic(button_metadata),
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
                topic_msg=b"long click",
                topic_pub=self._get_topic(button_metadata),
            )
            if "long_click_action" in button_metadata:
                self.samsung_ir_transmitter.activate(
                    button_metadata["long_click_action"]
                )

        return execute
        # self.samsung_ir_transmitter.activate("source")

    def _get_topic(self, button_metadata: dict):
        return "coffee_table/button/{0}".format(button_metadata["pin_nb"]).encode(
            "utf-8"
        )

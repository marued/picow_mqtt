import uasyncio
import network
import time
import machine
from umqtt.simple import MQTTClient


class MQTT:
    def __init__(self):
        self.board_led = machine.Pin("LED", mode=machine.Pin.OUT)
        self._callbacks = []

    def register_callback(self, message_identifier, callback):
        self._callbacks.append((message_identifier, callback))

    def connect(self, ssid, password):
        # Connect to WLAN
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.wlan.connect(ssid, password)

        while self.wlan.isconnected() == False:
            print("Waiting for connection...")
            time.sleep(1)

        ip = self.wlan.ifconfig()[0]
        print(f"Connected on {ip}")
        self.blink()
        return ip

    def mqtt_connect(
        self,
        mqtt_server,
        mqtt_port,
        client_username,
        client_psw,
        client_id,
    ):
        self.client = MQTTClient(
            client_id,
            mqtt_server,
            port=mqtt_port,
            user=client_username,
            password=client_psw,
            keepalive=3600,
        )
        self.client.set_callback(self._on_message_received)
        self.client.connect()
        print("Connected to %s MQTT Broker" % (mqtt_server))
        return self.client

    def reset_and_reconnect(self):
        print("Failed to connect to the MQTT Broker. Reconnecting...")
        time.sleep(5)
        machine.reset()

    def blink(self):
        self.board_led.value(1)
        timer = machine.Timer()
        timer.init(
            mode=machine.Timer.ONE_SHOT,
            period=800,
            callback=lambda t: self.board_led.value(0),
        )

    def publish(self, topic_pub=b"homeassistant/test", topic_msg=b"Button pressed!"):
        self.client.publish(topic_pub, topic_msg)

        # Blink the board LED to indicate a publish
        self.blink()
        print("Publishing to MQTT Broker {0}: {1}".format(topic_pub, topic_msg))

    def start_msg_check(self, topic_sub=b"homeassistant/test"):
        self.client.subscribe(topic_sub)
        print("Subscribed to {0} topic".format(topic_sub))
        uasyncio.create_task(self._check_msg_loop())

    async def _check_msg_loop(self):
        print("mqtt start check msg loop")
        while True:
            try:
                self.client.check_msg()
            except OSError as e:
                print("Failed to check MQTT message: {0}".format(e))
                self.reset_and_reconnect()
            await uasyncio.sleep(0.1)

    def _on_message_received(self, topic, message):
        print("Topic: {0}, Message: {1}".format(topic, message))
        # Blink the board LED to indicate a message
        self.blink()

        for message_identifyer, callback in self._callbacks:
            print("message_identifyer: ", message_identifyer, "message: ", message)
            if message_identifyer == message:
                callback(topic, message)

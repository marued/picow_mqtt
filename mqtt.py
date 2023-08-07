import time
import machine
from mqtt_as.mqtt_as import MQTTClient, config


class MQTT:
    def __init__(self):
        self.board_led = machine.Pin("LED", mode=machine.Pin.OUT)
        self._callbacks = []
        self.foo = {"foo": "bar"}

    def register_callback(self, message_identifier, callback):
        self._callbacks.append((message_identifier, callback))

    async def mqtt_connect(
        self,
        mqtt_server,
        mqtt_port,
        client_username,
        client_psw,
        client_id,
        ssid,
        password,
    ):
        config["client_id"] = client_id
        config["server"] = mqtt_server
        config["port"] = mqtt_port
        config["user"] = client_username
        config["password"] = client_psw
        config["subs_cb"] = self._on_message_received
        config["connect_coro"] = self.start_msg_check
        config["ssid"] = ssid
        config["wifi_pw"] = password
        self.client = MQTTClient(config)
        await self.client.connect()
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

    async def publish(self, topic_pub=b"coffee_table", topic_msg=b"Button pressed!"):
        await self.client.publish(topic_pub, topic_msg)

        # Blink the board LED to indicate a publish
        self.blink()
        print("Publishing to MQTT Broker {0}: {1}".format(topic_pub, topic_msg))

    async def start_msg_check(self, client, topic_sub="coffee_table/post"):
        print("Is Connected: {}".format(client.isconnected()))
        print(topic_sub)
        await client.subscribe(topic_sub)
        print("Subscribed to {0} topic".format(topic_sub))

    def _on_message_received(self, topic, message, retained):
        try:
            print(
                "Topic: {0}, Message: {1}, Retained: {2}".format(
                    topic, message, retained
                )
            )
            # Blink the board LED to indicate a message
            self.blink()

            # Execute the callback associated to the message
            for message_identifyer, callback in self._callbacks:
                print("message_identifyer: ", message_identifyer, "message: ", message)
                if message_identifyer == message:
                    callback(topic, message)
        except Exception as e:
            print("Error on message received: {0}".format(e))
            self.reset_and_reconnect()

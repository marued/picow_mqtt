from cofee_table.table_module import TableModule
import uasyncio
import machine


async def start():
    print("Executing main")
    table_module = TableModule(
        [
            {
                "pin_nb": 21,
                "heptic_pin_nb": 12,
                "single_click_action": "tv_power",
                # "double_click_action": "volume_down",
                # "long_click_action": "power",
            },
            {
                "pin_nb": 19,
                "heptic_pin_nb": 12,
                "single_click_action": "tv_volume_up",
            },
            {
                "pin_nb": 16,
                "heptic_pin_nb": 12,
                "single_click_action": "tv_volume_down",
            },
            {
                "pin_nb": 17,
                "heptic_pin_nb": 12,
                "single_click_action": "tv_source",
            },
        ],
        15,
    )
    try:
        table_module.connect()
        table_module.register_callbacks()
        table_module.mqtt_server.start_msg_check()
    except Exception as e:
        # table_module.mqtt_server.publish(b"coffee_table/error", str(e).encode("utf-8"))
        print("Error during initialisation time.: {0}".format(e))
        machine.reset()

    while True:
        await uasyncio.sleep(100)


if __name__ == "__main__":
    # Need to run subrutine so it can yield to
    # others and not exit the main thread
    uasyncio.run(start())

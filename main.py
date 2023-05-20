from cofee_table.table_module import TableModule
import uasyncio


async def start():
    print("Executing main")
    table_module = TableModule(
        [
            {"pin_nb": 17, "heptic_pin_nb": 2, "long_click_action": "power"},
            {"pin_nb": 18, "heptic_pin_nb": 3},
        ],
        15,
    )
    table_module.connect()
    table_module.register_callbacks()
    table_module.mqtt_server.start_msg_check()
    while True:
        await uasyncio.sleep(100)


if __name__ == "__main__":
    # Need to run subrutine so it can yield to
    # others and not exit the main thread
    uasyncio.run(start())

import time

time.sleep(1)  # somehow it's recomended by mqtt_as...?
from cofee_table.table_module import TableModule
import uasyncio
import machine
import gc

global table_module


async def heart_beat():
    board_led = machine.Pin("LED", mode=machine.Pin.OUT)
    while True:
        print("heart beat")
        board_led.value(1)
        await uasyncio.sleep_ms(200)
        board_led.value(0)
        await uasyncio.sleep(10)


async def run_gc():
    while True:
        gc.collect()
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
        await uasyncio.sleep(120)


def set_global_exception():
    def handle_exception(loop, context):
        import sys

        sys.print_exception(context["exception"])
        sys.exit()

    loop = uasyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)


async def start():
    set_global_exception()

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
        table_module.register_callbacks()
        await table_module.connect()
        table_module.async_tasks.add(run_gc())
        table_module.async_tasks.add(heart_beat())
        result = await uasyncio.gather(*table_module.async_tasks)
        print("result: ", result)
        print("End of main")
    finally:
        if hasattr(table_module.mqtt_server, "client"):
            table_module.mqtt_server.client.close()


if __name__ == "__main__":
    try:
        uasyncio.run(start())
    finally:
        uasyncio.new_event_loop()

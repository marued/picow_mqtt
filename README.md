# picow_mqtt
Mqtt project done in micro python for device such as the Pi Pico W to integrate a custom IR blaster and multiple touch buttons with MQTT for smart home DIY project.

# IR remote
The IR code was copied from https://github.com/peterhinch/micropython_ir. For ease of installation on ESP device the folders ir_tx and ir_rx were copied over. For mode details and great documentation on how it works, got read the different readme files on that project.

# Async MQTT 
The library used for MQTT was recommended by the `uasync` (https://github.com/peterhinch/micropython-async/blob/master/v3/docs/TUTORIAL.md#21-program-structure) lib: `mqtt_as` (https://github.com/peterhinch/micropython-mqtt/blob/master/mqtt_as/README.md#22-installation). In this project, the files mqtt_as.py and mqtt_local.py were copied over to the folder `/lib/mqtt_as/` on the pico w. 

# Installation
Using THONY: Copy over all files in `/cofee_table` and the folder `ir_tx` as well to `/cofee_table` on the pico w. Copy the main to the root of the pico w. Copy over mqtt_as.py and mqtt_local.py to `/lib/mqtt_as`. When the main.py file will run automatically when the device is powered on. 
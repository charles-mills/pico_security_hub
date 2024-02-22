import asyncio

from pico_security_hub.config import networking
from pico_security_hub.config import config_vars as master
from pico_security_hub.controllers import control_display


async def get_data():
    str_to_bool = {
        "ON": True,
        "OFF": False
    }

    while True:
        update = networking.mqtt_link.checkForUpdates()

        while update is not None:
            config_var = update[0].split("crjm/feeds/", 1)[1]  # Remove the /feeds/ part of the string
            master.config_dict[config_var] = str_to_bool[update[1]]
            update = networking.mqtt_link.checkForUpdates()

        await asyncio.sleep(10)


async def main():
    await get_data()

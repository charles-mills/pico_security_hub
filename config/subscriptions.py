import asyncio

from pico_security_hub.config import networking
from pico_security_hub.config import config_vars as master
from pico_security_hub.controllers import control_display


async def get_data():
    while True:
        updates = []
        update = networking.mqtt_link.checkForUpdates()

        while update:
            """ Remove the /feeds/ part of the string to get the config variable name. """
            config_var = update[0].split("crjm/feeds/", 1)[1]
            updates.append((config_var, master.str_to_bool[update[1]]))
            update = networking.mqtt_link.checkForUpdates()

        if updates:
            for config_var, value in updates:
                master.config_dict[config_var] = value
            master.write_config()

        await asyncio.sleep(5)


async def main():
    await get_data()

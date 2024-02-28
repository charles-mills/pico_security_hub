import asyncio

from pico_security_hub.config import networking
from pico_security_hub.config import config_vars as master
from pico_security_hub.controllers import control_display


async def parse_updates():
    updates = []
    update = networking.mqtt_link.checkForUpdates()

    while update:
        config_var = update[0].split("crjm/feeds/", 1)[1]
        updates.append((config_var, master.adafruit_conversion_dict[update[1]]))
        update = networking.mqtt_link.checkForUpdates()

    return updates


async def update_config(updates):
    if updates:
        for config_var, value in updates:
            master.config_dict[config_var] = value
        master.write_config()


async def get_data():
    if not master.DEBUG_MODE:
        while True:
            updates = await parse_updates()
            await update_config(updates)
            await asyncio.sleep(2.5)
            await asyncio.sleep(0)  # Yield control to the event loop


async def main():
    await get_data()

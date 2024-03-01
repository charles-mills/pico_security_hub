import asyncio

from pico_security_hub.config import networking
from pico_security_hub.config import configuration


async def parse_updates():
    updates = []
    update = networking.mqtt_link.checkForUpdates()

    while update:
        config_var = update[0].split("crjm/feeds/", 1)[1]
        updates.append(
            (config_var, configuration.config_manager.ADAFRUIT_CONVERSION_DICT[update[1]]))
        update = networking.mqtt_link.checkForUpdates()

    return updates


async def update_config(updates):
    if updates:
        for config_var, value in updates:
            configuration.config_manager.config_dict[config_var] = value
        configuration.config_manager.write_config()


async def get_data():
    if not configuration.config_manager.DEBUG_MODE:
        while True:
            updates = await parse_updates()
            await update_config(updates)
            await asyncio.sleep(2.5)
            await asyncio.sleep(0)  # Yield control to the event loop


async def main():
    await get_data()

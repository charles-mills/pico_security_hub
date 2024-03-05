import asyncio
import microcontroller

from pico_security_hub.networking import mqtt_handler
from pico_security_hub.config import configuration
from pico_security_hub.controllers import control_led


async def publ_cpu_temp():
    while True:
        if configuration.config_manager.MASTER_LOOP and configuration.config_manager.config_dict["temperature_publish"]:
            cpu_temp = microcontroller.cpu.temperature
            mqtt_handler.publ_data(mqtt_handler.mqtt_link,
                                 "core_temperature", cpu_temp, mute=True)
            await control_led.send_colour()
        await asyncio.sleep(5)


async def main():
    await asyncio.gather(publ_cpu_temp())


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import microcontroller

from pico_security_hub.config import networking
from pico_security_hub.config import config_vars as master
from pico_security_hub.controllers import control_led


async def publ_cpu_temp():
    while True:
        if master.master_loop and master.config_dict["temperature_publish"]:
            cpu_temp = microcontroller.cpu.temperature
            networking.publ_data(networking.mqtt_link, "core_temperature", cpu_temp, mute=True)
            await control_led.send_colour()
        await asyncio.sleep(5)


async def main():
    await asyncio.gather(publ_cpu_temp())


if __name__ == "__main__":
    asyncio.run(main())


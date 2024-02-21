import asyncio
import microcontroller

from pico_security_hub.config import networking
from pico_security_hub.config import config_vars as master


async def publ_cpu_temp():
    while True:
        if master.master_loop:
            cpu_temp = microcontroller.cpu.temperature
            networking.publ_data(networking.mqtt_link, "coreTemperature", cpu_temp, mute=True)
            await asyncio.sleep(5)


async def main():
    await asyncio.gather(publ_cpu_temp())


if __name__ == "__main__":
    asyncio.run(main())


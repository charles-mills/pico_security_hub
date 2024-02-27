import asyncio

from pico_security_hub.controllers import control_led
from pico_security_hub.config import config_vars as master


async def trigger(sensor, message, published=True):
    output = f"{sensor}: {message} - "

    if published:
        output += "Published to Adafruit IO"
        await control_led.send_colour()
    else:
        output += "Publishing is Disabled."

    master.log(output)

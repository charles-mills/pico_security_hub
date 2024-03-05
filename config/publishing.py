from pico_security_hub.controllers import control_led
from pico_security_hub.config import configuration


async def trigger(sensor, message, published=True):
    output = f"{sensor}: {message} - "

    if published:
        output += "Published to Adafruit IO"
        await control_led.send_colour()
    else:
        output += "Publishing is Disabled."

    configuration.config_manager.log(output)

import asyncio

from pico_security_hub.config import configuration
from Unit19Modules.neopixel import board_neoPixel

neo = board_neoPixel.neoPixel()

colour_in_queue = False
alarm_active = False

colour_to_func = {
    "red": neo.setRed(20),
    "blue": neo.setBlue(20),
    "green": neo.setGreen(20),
    "yellow": neo.setYellow(20),
    "white": neo.setWhite(20),
}


def disable():
    configuration.config_manager.config_dict["LED_enabled"] = False
    neo.off()


def led_active():
    if not configuration.config_manager.config_dict["LED_enabled"]:
        neo.off()
        return False
    return True


async def trigger_alarm():
    while True:
        if led_active():
            if alarm_active:
                neo.setRed(20)
                await asyncio.sleep(0.1)
                neo.setBlue(20)
                await asyncio.sleep(0.1)
            else:
                await asyncio.sleep(0.25)
        else:
            await asyncio.sleep(0.25)


async def send_colour(time=0.1):
    global colour_in_queue

    if led_active() and not alarm_active:
        neo.setMagenta(20)
        colour_in_queue = True
        await asyncio.sleep(time)
        colour_in_queue = False


async def idle():
    while True:
        if led_active() and not colour_in_queue and not alarm_active:
            neo.setWhite(10)
        await asyncio.sleep(0.25)


async def main():
    await asyncio.gather(idle(), trigger_alarm())

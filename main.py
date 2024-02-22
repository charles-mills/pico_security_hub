import asyncio
import sys
from pico_security_hub.config import boot
from pico_security_hub.sensors import motion_detection
from pico_security_hub.sensors import hardware_temp
from pico_security_hub.sensors import local_temp
from pico_security_hub.sensors import uptime
from pico_security_hub.controllers import control_buttons
from pico_security_hub.controllers import control_display
from pico_security_hub.controllers import control_led
from pico_security_hub.controllers import control_buzzer
from pico_security_hub.config import config_vars as master
from pico_security_hub.config import subscriptions


async def start_offline():
    print("\tNetworking is disabled, only the display will be active.")
    buttons_task = asyncio.create_task(control_buttons.main())
    display_task = asyncio.create_task(control_display.main())
    led_task = asyncio.create_task(control_led.main())
    await asyncio.gather(buttons_task, display_task, led_task)


async def start_online():
    boot.main()
    # Start the subscription task
    subscription_task = asyncio.create_task(subscriptions.main())
    # Start the motion detection sensor
    motion_task = asyncio.create_task(motion_detection.main())
    # Start the hardware temperature sensor
    hardware_task = asyncio.create_task(hardware_temp.main())
    # Start the local temperature and humidity sensor
    local_task = asyncio.create_task(local_temp.main())
    # Start the buttons task to control the display
    buttons_task = asyncio.create_task(control_buttons.main())
    # Start the display task
    display_task = asyncio.create_task(control_display.main())
    # Start the LED task
    led_task = asyncio.create_task(control_led.main())
    # Start monitoring uptime task
    uptime_task = asyncio.create_task(uptime.main())
    # Start the buzzer task to output sound
    buzzer_task = asyncio.create_task(control_buzzer.main())

    control_buzzer.queue_tunes["start"] = True

    await asyncio.gather(subscription_task, motion_task, hardware_task,
                         local_task, buttons_task, display_task, led_task, uptime_task, buzzer_task)


async def main():
    try:
        if master.networking_enabled:
            await start_online()
        else:
            await start_offline()
    except RuntimeError:
        await start_offline()
        

if __name__ == "__main__":
    print("System Starting")
    sys.exit(asyncio.run(main()))
    
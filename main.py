import asyncio
import sys
from pico_security_hub.config import boot
from pico_security_hub.sensors import motion_detection
from pico_security_hub.sensors import hardware_temp
from pico_security_hub.sensors import local_temp
from pico_security_hub.controllers import control_buttons
from pico_security_hub.controllers import control_display
from pico_security_hub.config import config_vars as master


async def main():
    if master.networking_enabled:
        boot.main()
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
        await asyncio.gather(motion_task, hardware_task, local_task, buttons_task, display_task)
    else:
        print("\tNetworking is disabled, only the display will be active.")
        buttons_task = asyncio.create_task(control_buttons.main())
        display_task = asyncio.create_task(control_display.main())
        await asyncio.gather(buttons_task, display_task)


if __name__ == "__main__":
    print("System Starting")
    sys.exit(asyncio.run(main()))
    
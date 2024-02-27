import asyncio
import sys

from pico_security_hub.config import boot, config_vars as master, networking, subscriptions
from pico_security_hub.controllers import control_buzzer, control_buttons, control_display, control_led
from pico_security_hub.sensors import hardware_temp, local_temp, motion_detection, uptime


async def start_offline():
    """Start the system in offline mode, only initialising the display, buttons, and LED."""
    master.NETWORKING_ENABLED = False
    print("\tNetworking is disabled, only the display will be active.")
    await asyncio.gather(control_buttons.main(), control_display.main(), control_led.main())


async def start_online():
    """Start the system in online mode, initialising all components."""
    boot.main()  # Run the boot sequence, configuring networking in the process.
    master.get_vars()  # Fetch configuration variables from the local JSON file.
    networking.publ_initial_config()  # Publish the initial configuration to the MQTT broker.
    control_buzzer.queue.append("start")   # Queue the start-up tune if the buzzer is enabled.

    await asyncio.gather(subscriptions.main(), motion_detection.main(), hardware_temp.main(),
                         local_temp.main(), control_buttons.main(), control_display.main(),
                         control_led.main(), uptime.main(), control_buzzer.main())


async def main():
    """Main function to start the system."""
    print("System Starting")

    try:
        if master.NETWORKING_ENABLED:
            await start_online()
        else:
            await start_offline()
    except RuntimeError:  # Occurs when the system is unable to connect to the MQTT broker.
        print("RuntimeError occurred, falling back to offline mode.")
        await start_offline()
    except Exception as e:  # Catch-all exception to prevent the system from crashing.
        print(f"Unexpected error occurred: {e}, falling back to offline mode.")
        await start_offline()
    else:
        print("System started successfully.")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))


import asyncio
import sys

from pico_security_hub.boot import boot_sequence
from pico_security_hub.config import configuration, networking, subscriptions
from pico_security_hub.controllers import control_buzzer, control_buttons, control_display, control_led
from pico_security_hub.sensors import hardware_temp, local_temp, motion_detection, uptime


async def start_system_offline(config_manager=configuration.config_manager):
    """Start the system in offline mode, only initialising the display, buttons, and LED."""
    config_manager.NETWORKING_ENABLED = False
    print("\tNetworking is disabled, only the display will be active.")
    await asyncio.gather(control_buttons.main(), control_display.main(), control_led.main())


async def start_system_online(config_manager=configuration.config_manager):
    """Start the system in online mode, initialising all components."""
    boot_sequence.main()  # Run the boot sequence, configuring networking in the process.
    # Fetch configuration variables from the local JSON file.
    config_manager.get_vars()
    # Publish the initial configuration to the MQTT broker.
    networking.publ_initial_config()
    # Queue the start-up tune if the buzzer is enabled.
    control_buzzer.queue.append("start")

    await asyncio.gather(subscriptions.main(), motion_detection.main(), hardware_temp.main(),
                         local_temp.main(), control_buttons.main(), control_display.main(),
                         control_led.main(), uptime.main(), control_buzzer.main())


async def main():
    """Main function to start the system."""
    config_manager = configuration.config_manager
    print("System Starting")

    if config_manager.DEBUG_MODE:
        print("\tDebug mode is enabled, no data will be fetched from the MQTT broker and file I/O is disabled.")

    try:
        if config_manager.NETWORKING_ENABLED:
            await start_system_online()
        else:
            await start_system_offline()
    except RuntimeError:  # Occurs when the system is unable to connect to the MQTT broker.
        print("RuntimeError occurred, falling back to offline mode.")
        await start_system_offline()
    except Exception as e:  # Catch-all exception to prevent the system from crashing.
        print(f"Unexpected error occurred: {e}, falling back to offline mode.")
        await start_system_offline()
    else:
        print("System started successfully.")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

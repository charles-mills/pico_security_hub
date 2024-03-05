import asyncio
import time
import sys

from pico_security_hub.boot import boot_sequence
from pico_security_hub.config import configuration, bot
from pico_security_hub.networking import mqtt_handler, subscriptions
from pico_security_hub.controllers import control_buzzer, control_buttons, control_display, control_led
from pico_security_hub.sensors import hardware_temp, local_temp, motion_detection, uptime


def handle_exception_and_quit(error):
    if error == RuntimeError:
        print("RuntimeError occurred, check system components are connected.")
        control_led.neo.setRed(10)
        time.sleep(1)
        control_led.neo.setYellow(10)
        sys.exit(1)


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
    mqtt_handler.publ_initial_config()
    # Queue the start-up tune if the buzzer is enabled.
    control_buzzer.queue.append("start")

    await asyncio.gather(subscriptions.main(), motion_detection.main(), hardware_temp.main(),
                         local_temp.main(), control_buttons.main(), control_display.main(),
                         control_led.main(), uptime.main(), control_buzzer.main(), bot.main())


def get_config_manager():
    config_manager = configuration.config_manager

    if config_manager.DEBUG_MODE:
        print("\tDebug mode is enabled, no data will be fetched from the MQTT broker and file I/O is disabled.")

    return configuration.config_manager


async def main():
    """Main function to start the system."""
    config_manager = get_config_manager()
    print("System Starting")

    try:
        if config_manager.NETWORKING_ENABLED:
            await start_system_online()
        else:
            await start_system_offline()
    except RuntimeError:  # Occurs when the system is unable to connect
        # to the MQTT broker or components are disconnected.
        handle_exception_and_quit(RuntimeError)
    except Exception as e:  # Catch-all exception to prevent the system from crashing.
        print(f"Unexpected error occurred: {e}, falling back to offline mode.")
        await start_system_offline()
    else:
        print("System started successfully.")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

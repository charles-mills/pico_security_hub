import sys
import asyncio
import board
import pulseio

from pico_security_hub.networking import mqtt_handler, publishing
from pico_security_hub.config import configuration
from pico_security_hub.controllers import control_led, control_buzzer

HIGH_SENSITIVE_FLAGS = 2
LOW_SENSITIVE_FLAGS = 4

motion_detected = False
expected_range_cm = 0
sonic_ranger = pulseio.PulseIn(board.GP3)


def check_motion_sensitive():
    """
    This function checks if the motion detection is set to be sensitive or not.
    """
    if configuration.config_manager.config_dict["motion_sensitive"]:
        return HIGH_SENSITIVE_FLAGS
    return LOW_SENSITIVE_FLAGS


async def handle_motion_publishing(motion_detection_flags, allowed_flags):
    if motion_detection_flags >= allowed_flags:
        motion_detection_flags = 0
        if configuration.config_manager.config_dict["motion_publish"]:
            mqtt_handler.publ_data(
                mqtt_handler.mqtt_link, "motion_detected", "Motion Detected!", mute=True)
            await publishing.trigger("Motion Detection", "Motion Detected")
        else:
            await publishing.trigger("Motion Detection", "Motion Detected", False)
    return motion_detection_flags


def handle_motion_detection(actual_dist_cm, motion_detection_flags):
    global motion_detected

    if actual_dist_cm < expected_range_cm:
        motion_detection_flags += 1
        control_led.alarm_active = True
        motion_detected = True
        control_buzzer.queue.append("alarm")
    elif actual_dist_cm > expected_range_cm and motion_detection_flags > 0:
        motion_detection_flags -= 1
        control_led.alarm_active = False
        motion_detected = False
    else:
        motion_detection_flags = 0
        control_led.alarm_active = False
        motion_detected = False
    return motion_detection_flags


async def measure_distance():
    """
    This function measures the distance using the sonic ranger sensor.

    :return actual_dist_cm: The measured distance in centimeters.
    """
    sonic_ranger.clear()
    sonic_ranger.resume(1)
    await asyncio.sleep(0.1)
    sonic_ranger.pause()

    actual_dist_cm = sonic_ranger[0] * 0.017

    return actual_dist_cm


async def check_motion():
    """
    This function continuously checks for motion and updates the `motion_detected` variable.
    It uses the sonic ranger sensor to measure the distance and compares it with the expected range.
    If the measured distance is less than the expected range, it considers that a motion is detected.
    """
    global expected_range_cm

    motion_detection_flags = 0
    expected_range_cm -= expected_range_cm / 10

    while True:
        if configuration.config_manager.MASTER_LOOP and configuration.config_manager.config_dict["motion_enabled"]:
            allowed_flags = check_motion_sensitive()
            actual_dist_cm = await measure_distance()
            motion_detection_flags = handle_motion_detection(actual_dist_cm, motion_detection_flags)
            motion_detection_flags = await handle_motion_publishing(motion_detection_flags, allowed_flags)
        await asyncio.sleep(0.5)


async def get_baseline(loops):
    """
    This function calculates the baseline distance for the motion detection.

    :param loops: The number of measurements to take.
    :return centre_result: The median (not yet sorted) distance of the measurements.

    """
    configuration.config_manager.config_dict["motion_enabled"] = False
    results = []

    for _ in range(loops):
        try:
            results.append(await measure_distance())
        except IndexError:
            pass

    centre_result = results[int(loops / 2)]  # This calculation should be improved by calculating median
    print(f"Motion Detection: Baseline Test Completed - {centre_result}cm")
    configuration.config_manager.config_dict["motion_enabled"] = True
    return centre_result


async def main():
    global expected_range_cm

    try:
        baseline = await asyncio.gather(asyncio.create_task(get_baseline(10)))
        expected_range_cm = baseline[0]
    except Exception as e:
        print(f"An error occurred while getting the baseline: {e}")
        return

    try:
        await asyncio.gather(asyncio.create_task(check_motion()))
    except Exception as e:
        print(f"An error occurred while checking for motion: {e}")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

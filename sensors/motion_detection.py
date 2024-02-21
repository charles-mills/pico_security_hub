import sys
import asyncio
import board
import pulseio

from pico_security_hub.config import networking
from pico_security_hub.config import config_vars as master
from pico_security_hub.config import publishing
from pico_security_hub.controllers import control_led


motion_detected = False
expected_range_cm = 0
sonic_ranger = pulseio.PulseIn(board.GP3)


async def get_baseline(loops):
    global motion_detected

    master.motion_enabled = False
    results = []

    for x in range(loops):
        sonic_ranger.clear()
        sonic_ranger.resume(1)
        await asyncio.sleep(0.1)
        sonic_ranger.pause()

        results.append(sonic_ranger[0] * 0.017)

    centre_result = results[int(loops/2)]
    print(f"Motion Detection: Baseline Test Completed - {centre_result}cm")
    master.motion_enabled = True
    return centre_result


async def check_motion():
    global motion_detected
    global expected_range_cm

    motion_detection_flags = 0
    expected_range_cm -= expected_range_cm / 10

    while True:
        if master.master_loop and master.config_dict["motion_enabled"]:
            allowed_flags = 5
            
            if master.config_dict["motion_sensitive"]:
                allowed_flags = 2
            
            sonic_ranger.clear()
            sonic_ranger.resume(1)
            await asyncio.sleep(0.25)
            sonic_ranger.pause()
    
            actual_dist_cm = sonic_ranger[0] * 0.017

            if actual_dist_cm < expected_range_cm:
                motion_detection_flags += 1
                control_led.alarm_active = True
                motion_detected = True
            elif actual_dist_cm > expected_range_cm and motion_detection_flags > 0 :
                motion_detection_flags -= 1
                control_led.alarm_active = False
                motion_detected = False
            else:
                motion_detection_flags = 0
                control_led.alarm_active = False
                motion_detected = False


            if motion_detection_flags >= allowed_flags:
                motion_detection_flags = 0
                if master.config_dict["motion_publish"]:
                    networking.publ_data(networking.mqtt_link, "motionDetected", "Motion Detected!", mute=True)
                    await publishing.trigger("Motion Detection", "Motion Detected")
                else:
                    await publishing.trigger("Motion Detection", "Motion Detected", False)
        else:
            await asyncio.sleep(0.5)


async def main():
    global expected_range_cm

    baseline = await asyncio.gather(asyncio.create_task(get_baseline(10)))
    expected_range_cm = baseline[0]
    
    await asyncio.gather(asyncio.create_task(check_motion()))


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

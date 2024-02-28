import board
import asyncio
import digitalio
import sys

from pico_security_hub.controllers import control_display as display
from pico_security_hub.controllers import control_led
from adafruit_debouncer import Debouncer


def make_pin_reader(pin):
    io = digitalio.DigitalInOut(pin)
    io.direction = digitalio.Direction.INPUT
    io.pull = digitalio.Pull.UP
    return lambda: io.value


async def process_cycle_button(cycle):
    cycle.update()
    if display.info["in_options"] and cycle.fell:
        display.info["cycle_highlighted"] = True


async def process_select_button(select):
    select.update()
    if display.info["in_options"] and select.fell:
        display.info["selection_changed"] = True


async def process_cycle_menu_button(cycle_menu):
    cycle_menu.update()
    if cycle_menu.fell:
        if display.info["display_selector_option"] >= display.info["max_index_options"]:
            display.info["display_selector_option"] = 0
        else:
            display.info["display_selector_option"] += 1


async def process_forfeit_button(forfeit):
    forfeit.update()
    if forfeit.fell:
        display.info["exit_program"] = True
        control_led.disable()
        print("Program is ending in 1 second...")
        await asyncio.sleep(1)
        sys.exit()


async def process_buttons(cycle, select, cycle_menu, forfeit):
    button_functions = {
        cycle: process_cycle_button,
        select: process_select_button,
        cycle_menu: process_cycle_menu_button,
        forfeit: process_forfeit_button
    }

    while True:
        for button, function in button_functions.items():
            await function(button)
        await asyncio.sleep(0.05)


async def main():
    cycle_btn = Debouncer(make_pin_reader(board.GP20))
    select_btn = Debouncer(make_pin_reader(board.GP21))
    cycle_menu_btn = Debouncer(make_pin_reader(board.GP22))
    forfeit_btn = Debouncer(make_pin_reader(board.GP5))

    buttons_task = asyncio.create_task(process_buttons(
        cycle_btn, select_btn, cycle_menu_btn, forfeit_btn))

    await asyncio.gather(buttons_task)


if __name__ == "__main__":
    asyncio.run(main())

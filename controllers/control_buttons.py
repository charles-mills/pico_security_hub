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


async def process_buttons(cycle, select, cycle_menu, forfeit):
    while True:
        cycle.update()
        select.update()
        cycle_menu.update()
        forfeit.update()

        if display.in_options:
            if cycle.fell:
                display.cycle_highlighted = True
            elif select.fell:
                display.selection_changed = True

        if cycle_menu.fell:
            if display.display_selector_option >= display.max_index_options:
                display.display_selector_option = 0
            else:
                display.display_selector_option += 1
        elif forfeit.fell:
            display.exit_program = True
            control_led.disable()
            print("Program is ending in 1 second...")
            await asyncio.sleep(1)
            sys.exit()
        await asyncio.sleep(0.05)


async def main():
    cycle_btn = Debouncer(make_pin_reader(board.GP20))
    select_btn = Debouncer(make_pin_reader(board.GP21))
    cycle_menu_btn = Debouncer(make_pin_reader(board.GP22))
    forfeit_btn = Debouncer(make_pin_reader(board.GP5))

    buttons_task = asyncio.create_task(process_buttons(cycle_btn, select_btn, cycle_menu_btn, forfeit_btn))

    await asyncio.gather(buttons_task)


if __name__ == "__main__":
    asyncio.run(main())
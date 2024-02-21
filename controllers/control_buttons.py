import board
import asyncio
import digitalio

from pico_security_hub.controllers import control_display as display
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

        if cycle.fell:
            display.cycle_highlighted = True
        elif select.fell:
            display.selection_changed = True
        elif cycle_menu.fell:
            display.display_selector_option = True
        elif forfeit.fell:
            display.exit_program = True

        await asyncio.sleep(0.1)


async def main():
    cycle_btn = Debouncer(make_pin_reader(board.GP20))
    select_btn = Debouncer(make_pin_reader(board.GP21))
    cycle_menu_btn = Debouncer(make_pin_reader(board.GP22))
    forfeit_btn = Debouncer(make_pin_reader(board.GP5))

    buttons_task = asyncio.create_task(process_buttons(cycle_btn, select_btn, cycle_menu_btn, forfeit_btn))

    await asyncio.gather(buttons_task)

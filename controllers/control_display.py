from Unit19Modules.monochromeDisplay import grove_display

import asyncio

from pico_security_hub.controllers import display_class
from pico_security_hub.config import networking


# Global variables

loop = True
selection_changed = False
cycle_highlighted = False
exit_program = False
display_selector_option = 1


async def respond_to_buttons(display, menu, title, label_1, label_2, label_3):
    global loop, selection_changed, cycle_highlighted, exit_program, display_selector_option

    print("running")

    while True:
        if loop:
            if cycle_highlighted:
                cycle_highlighted = False
                menu.cycle_highlighted()
                print(menu.current_highlighted, menu.highlighted_index)
            if exit_program:
                loop = False
                display.clearScreen()
                await asyncio.sleep(0.5)
                display.closeDisplay()
                await asyncio.sleep(0.5)

            display_visible_highlights(display, menu, title, label_1, label_2, label_3)
        await asyncio.sleep(0.05)


def display_visible_highlights(display, menu, title, label_1, label_2, label_3):
    to_display = menu.get_current_list()

    display.updateLabelText(title, display_class.capitalise_first(menu.current_option) + " Menu")

    try:
        display.updateLabelText(label_1, to_display[0])
    except IndexError:
        display.updateLabelText(label_1, "")
    try:
        display.updateLabelText(label_2, to_display[1])
    except IndexError:
        display.updateLabelText(label_2, "")
    try:
        display.updateLabelText(label_3, to_display[2])
    except IndexError:
        display.updateLabelText(label_3, "")


async def main():
    menu = display_class.VisibleMenu()
    display = grove_display.BitmapDisplay(1)

    title = display.addLabel(8, 0, 1, "")
    label_1 = display.addLabel(8, 15, 1, "")
    label_2 = display.addLabel(8, 30, 1, "")
    label_3 = display.addLabel(8, 45, 1, "")

    display_visible_highlights(display, menu, title, label_1, label_2, label_3)

    respond_task = asyncio.create_task(respond_to_buttons(display, menu, title, label_1, label_2, label_3))

    await asyncio.gather(respond_task)

if __name__ == "__main__":
    asyncio.run(main())

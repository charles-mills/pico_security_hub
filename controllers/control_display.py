from Unit19Modules.monochromeDisplay import grove_display

import asyncio

from pico_security_hub.controllers import display_class
from pico_security_hub.sensors import motion_detection
from pico_security_hub.sensors import local_temp
from pico_security_hub.config import networking
from pico_security_hub.config import config_vars as master

# Global variables

loop = True
selection_changed = False
cycle_highlighted = False
exit_program = False
in_options = False
display_selector_option = 0
max_index_options = 4


def flood_detection_menu(display, title, label_1, label_2, label_3):
    global in_options

    in_options = False

    # Non-functional due to a lack of relevant sensors
    # Flood risk APIs are not usable due to cost

    display.updateLabelText(title, "Flood Detection")
    display.updateLabelText(label_1, "Overall Risk: Low")
    display.updateLabelText(label_2, "Water Levels: 0%")
    display.updateLabelText(label_3, "")


def fire_detection_menu(display, title, label_1, label_2, label_3):
    global in_options

    in_options = False

    display.updateLabelText(title, "Fire Detection")
    display.updateLabelText(label_1, f"Overall Risk: {local_temp.fire_risk()}")
    display.updateLabelText(label_2, f"Temperature: {local_temp.local_temp}°C")
    display.updateLabelText(label_3, f"Humidity: {local_temp.local_humidity}%")


def warnings_menu(display, title, label_1, label_2, label_3):
    global in_options

    in_options = False

    display.updateLabelText(title, "Warnings")
    display.updateLabelText(label_1, "No Warnings")
    display.updateLabelText(label_2, "")
    display.updateLabelText(label_3, "")


def motion_detection_menu(display, title, label_1, label_2, label_3):
    global in_options

    in_options = False

    display.updateLabelText(title, "Motion Detection")
    if master.motion_enabled:
        if motion_detection.motion_detected:
            display.updateLabelText(label_1, "Motion Detected!")
        else:
            display.updateLabelText(label_1, "No Motion Detected...")
    display.updateLabelText(label_2, "")
    display.updateLabelText(label_3, "")


async def display_menus(display, menu, title, label_1, label_2, label_3):
    while True:
        if display_selector_option == 0:
            motion_detection_menu(display, title, label_1, label_2, label_3)
        elif display_selector_option == 1:
            warnings_menu(display, title, label_1, label_2, label_3)
        elif display_selector_option == 2:
            flood_detection_menu(display, title, label_1, label_2, label_3)
        elif display_selector_option == 3:
            fire_detection_menu(display, title, label_1, label_2, label_3)
        elif display_selector_option == 4:
            display_visible_highlights(display, menu, title, label_1, label_2, label_3)

        await asyncio.sleep(0.25)


def confirm_change(var, menu, display, title, label_1, label_2, label_3):
    selection_index = menu.get_visible_options().index(menu.current_highlighted)

    if var:
        text = "Option is now True"
    else:
        text = "Option is now False"

    if selection_index == 0:
        display.updateLabelText(label_1, text)
    elif selection_index == 1:
        display.updateLabelText(label_2, text)
    elif selection_index == 2:
        display.updateLabelText(label_3, text)


def pause_display(display, title, label_1, label_2, label_3, text="Paused"):
    global loop

    loop = False
    display.updateLabelText(title, "")
    display.updateLabelText(label_1, "Display Paused")
    display.updateLabelText(label_2, text)
    display.updateLabelText(label_3, "")


async def toggle_var_and_confirm(var, menu, display, title, label_1, label_2, label_3):
    master.toggle_var(var)

    networking.publ_data(networking.mqtt_link, var, master.bool_to_str[master.config_dict[var]], True)
    confirm_change(master.config_dict[var], menu, display, title, label_1, label_2, label_3)
    await asyncio.sleep(0.5)


async def motion_re_initialise(display, title, label_1, label_2, label_3):
    global loop

    pause_display(display, title, label_1, label_2, label_3, "Re-initialising...")
    master.motion_detection_enabled = False
    baseline = await asyncio.create_task(motion_detection.get_baseline(15))
    motion_detection.expected_range_cm = (baseline - baseline / 10)
    master.motion_detection_enabled = True
    loop = True


async def respond_to_buttons(display, menu, title, label_1, label_2, label_3):
    global loop, selection_changed, cycle_highlighted, exit_program, display_selector_option

    while True:
        if loop:
            if cycle_highlighted:
                cycle_highlighted = False
                menu.cycle_highlighted()

            if selection_changed:
                selection_changed = False

                highlight_id = menu.current_option + "_" + menu.current_highlighted

                if menu.current_highlighted == "back":
                    # Go back to main menu
                    menu.set_current_option("main")

                elif highlight_id == "motion_re-initialise":
                    await motion_re_initialise(display, title, label_1, label_2, label_3)

                elif highlight_id in master.config_dict:
                    # If the current highlight is a toggleable option, toggle it
                    await toggle_var_and_confirm(highlight_id,
                                                 menu, display, title, label_1, label_2, label_3)

                elif menu.current_highlighted in menu.main_menu_highlights:
                    # If in main menu, select the option currently highlighted
                    menu.select_current_highlighted()
                else:
                    # Catch-all to send user back to main menu
                    menu.set_current_option("main")

            if exit_program:
                loop = False
                display.clearScreen()
                await asyncio.sleep(0.5)
                display.closeDisplay()
                await asyncio.sleep(0.5)
        await asyncio.sleep(0.05)


def set_title_text(display, title, menu):
    menu_title = display_class.capitalise_first(menu.current_option)
    menu_title = f"{menu_title} Menu {menu.highlighted_index + 1}/{len(menu.option_to_defaults[menu.current_option])}"

    display.updateLabelText(title, menu_title)


def display_visible_highlights(display, menu, title, label_1, label_2, label_3):
    global in_options

    in_options = True

    to_display = menu.get_current_list()
    set_title_text(display, title, menu)

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

    cycle_menu_task = asyncio.create_task(display_menus(display, menu, title, label_1, label_2, label_3))
    respond_task = asyncio.create_task(respond_to_buttons(display, menu, title, label_1, label_2, label_3))

    await asyncio.gather(respond_task, cycle_menu_task)


if __name__ == "__main__":
    asyncio.run(main())

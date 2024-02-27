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

previous_data = None

# Define a dictionary to map highlight_id to functions
highlight_id_to_function = {
    "motion_re-initialise": motion_detection.get_baseline(15),
    # Add other mappings here
}


def has_data_changed(new_data):
    """
    Checks if the new data is different from the previously stored data.

    :param new_data: The new data to be compared with the previous data.
    :return: True if the new data is different from the previous data, False otherwise.
    """
    global previous_data
    if new_data != previous_data:
        previous_data = new_data
        return True
    return False


def push_changed_data(display, title, label_1, label_2, label_3, new_data):
    """
    Updates the display labels if the new data is different from the previously stored data.

    :param display: The display object.
    :param title: The title label.
    :param label_1: The first label.
    :param label_2: The second label.
    :param label_3: The third label.
    :param new_data: The new data to be displayed.
    """
    for i in range(4):
        if has_data_changed(new_data[i]):
            display.updateLabelText(title, new_data[0])
            display.updateLabelText(label_1, new_data[1])
            display.updateLabelText(label_2, new_data[2])
            display.updateLabelText(label_3, new_data[3])

def flood_detection_menu(display, title, label_1, label_2, label_3):
    """
    Displays the flood detection menu.

    :param display: The display object.
    :param title: The title label.
    :param label_1: The first label.
    :param label_2: The second label.
    :param label_3: The third label.
    """
    global in_options

    in_options = False

    # Non-functional due to a lack of relevant sensors
    # Flood risk APIs are not usable due to cost

    new_data = ["Flood Detection", "Overall Risk: Low", "Water Levels: 0%", ""]
    push_changed_data(display, title, label_1, label_2, label_3, new_data)


def fire_detection_menu(display, title, label_1, label_2, label_3):
    """
    Displays the fire detection menu.

    :param display: The display object.
    :param title: The title label.
    :param label_1: The first label.
    :param label_2: The second label.
    :param label_3: The third label.
    """
    global in_options

    in_options = False

    new_data = ["Fire Detection", f"Overall Risk: {local_temp.fire_risk()}", f"Temperature: {local_temp.local_temp}°C", f"Humidity: {local_temp.local_humidity}%"]
    push_changed_data(display, title, label_1, label_2, label_3, new_data)


def warnings_menu(display, title, label_1, label_2, label_3):
    """
    Displays the warnings menu.

    :param display: The display object.
    :param title: The title label.
    :param label_1: The first label.
    :param label_2: The second label.
    :param label_3: The third label.
    """
    global in_options

    in_options = False

    new_data = ["Warnings", "No Warnings", "", ""]
    push_changed_data(display, title, label_1, label_2, label_3, new_data)


def motion_detection_menu(display, title, label_1, label_2, label_3):
    """
    Displays the motion detection menu.

    :param display: The display object.
    :param title: The title label.
    :param label_1: The first label.
    :param label_2: The second label.
    :param label_3: The third label.
    """
    global in_options

    in_options = False
    new_data = None

    display.updateLabelText(title, "Motion Detection")
    if master.config_dict["motion_enabled"]:
        if motion_detection.motion_detected:
            new_data = ["Motion Detection", "Motion Detected!", "", ""]
        else:
            new_data = ["Motion Detection", "No Motion Detected", "", ""]
    else:
        new_data = ["Motion Detection", "Option Disabled.", "", ""]

    push_changed_data(display, title, label_1, label_2, label_3, new_data)


async def display_menus(display, menu, title, label_1, label_2, label_3):
    """
    Continuously displays the selected menu.

    :param display: The display object.
    :param menu: The menu object.
    :param title: The title label.
    :param label_1: The first label.
    :param label_2: The second label.
    :param label_3: The third label.
    """
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

        await asyncio.sleep(0.1)


def confirm_change(var, menu, display, title, label_1, label_2, label_3):
    """
    Confirms the change of a variable and updates the display.

    :param var: The variable that has been changed.
    :param menu: The menu object.
    :param display: The display object.
    :param title: The title label.
    :param label_1: The first label.
    :param label_2: The second label.
    :param label_3: The third label.
    """
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
    """
    Pauses the display with a specified message.
    Used when timed functions are outgoing, such as motion detection re-initialisation.

    :param display: The display object.
    :param title: The title label.
    :param label_1: The first label.
    :param label_2: The second label.
    :param label_3: The third label.
    :param text: The text to be displayed when the display is paused.
    """
    global loop

    loop = False
    display.updateLabelText(title, "")
    display.updateLabelText(label_1, "Display Paused")
    display.updateLabelText(label_2, text)
    display.updateLabelText(label_3, "")


async def toggle_var_and_confirm(var, menu, display, title, label_1, label_2, label_3):
    """
    Toggles a variable, confirms the change (incl. publishing to Adafruit), and updates the display.

    :param var: The variable to be toggled.
    :param menu: The menu object.
    :param display: The display object.
    :param title: The title label.
    :param label_1: The first label.
    :param label_2: The second label.
    :param label_3: The third label.
    """
    master.toggle_var(var)
    networking.publ_data(networking.mqtt_link, var, master.bool_to_str[master.config_dict[var]], True)
    confirm_change(master.config_dict[var], menu, display, title, label_1, label_2, label_3)
    master.write_config()
    await asyncio.sleep(0.5)


async def motion_re_initialise(display, title, label_1, label_2, label_3):
    """
    Re-initialises the motion detection and updates the display.

    :param display: The display object.
    :param title: The title label.
    :param label_1: The first label.
    :param label_2: The second label.
    :param label_3: The third label.
    """
    global loop

    pause_display(display, title, label_1, label_2, label_3, "Re-initialising...")
    master.motion_detection_enabled = False
    baseline = await asyncio.create_task(motion_detection.get_baseline(15))
    motion_detection.expected_range_cm = (baseline - baseline / 10)
    master.motion_detection_enabled = True
    loop = True


async def process_selection(display, menu, title, label_1, label_2, label_3):
    global loop, selection_changed, cycle_highlighted, exit_program, display_selector_option

    if cycle_highlighted:
        cycle_highlighted = False
        menu.cycle_highlighted()

    if selection_changed:
        selection_changed = False

        highlight_id = menu.current_option + "_" + menu.current_highlighted

        if menu.current_highlighted == "back":
            # Go back to main menu
            menu.set_current_option("main")

        elif highlight_id in highlight_id_to_function:
            # If the current highlight is a function, call it
            await highlight_id_to_function[highlight_id](display, title, label_1, label_2, label_3)

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


async def respond_to_buttons(display, menu, title, label_1, label_2, label_3):
    global loop

    while True:
        if loop:
            await process_selection(display, menu, title, label_1, label_2, label_3)
        await asyncio.sleep(0.05)


def set_title_text(display, title, menu):
    """
    Sets the title of the display to the current menu.

    :param display: The display object.
    :param title: The title label.
    :param menu: The menu object.
    """
    menu_title = display_class.capitalise_first(menu.current_option)
    menu_title = f"{menu_title} Menu {menu.highlighted_index + 1}/{len(menu.option_to_defaults[menu.current_option])}"

    display.updateLabelText(title, menu_title)


def display_visible_highlights(display, menu, title, label_1, label_2, label_3):
    """
    Displays the currently visible options ("highlights") on the display.

    :param display: The display object.
    :param menu: The menu object.
    :param title: The title label.
    :param label_1: The first label.
    :param label_2: The second label.
    :param label_3: The third label.
    """
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
    """
    The main function that runs the display and responds to button presses.
    """
    menu = display_class.VisibleMenu()
    display = grove_display.BitmapDisplay(1)

    title = display.addLabel(8, 0, 1, "")
    label_1 = display.addLabel(8, 15, 1, "")
    label_2 = display.addLabel(8, 30, 1, "")
    label_3 = display.addLabel(8, 45, 1, "")

    tasks = [display_menus(display, menu, title, label_1, label_2, label_3),
             respond_to_buttons(display, menu, title, label_1, label_2, label_3)]

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())

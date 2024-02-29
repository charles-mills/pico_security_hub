import asyncio
from Unit19Modules.monochromeDisplay import grove_display

from pico_security_hub.controllers import display_class
from pico_security_hub.sensors import motion_detection
from pico_security_hub.sensors import local_temp
from pico_security_hub.config import networking
from pico_security_hub.config import config_vars as master

# Constants

SLEEP_TIME = 0.1  # Time to sleep between loops

# Global variables

settings = {
    "loop": True,
}

info = {
    "selection_changed": False,
    "cycle_highlighted": False,
    "exit_program": False,
    "in_options": False,
    "display_selector_option": 0,
    "max_index_options": 4,
    "previous_data": None,
    "last_visible_highlights": None,
    "last_selection_option": None,
}


def has_display_data_changed(new_data):
    """
    Checks if the new data is different from the previously stored data.

    :param new_data: The new data to be compared with the previous data.
    :return: True if the new data is different from the previous data, False otherwise.
    """
    global info
    if new_data != info["previous_data"]:
        info["previous_data"] = new_data
        return True
    return False


def push_display_data_changed(display, labels, new_data):
    """
    Updates the display labels if the new data is different from the previously stored data.

    :param display: The display object.
    :param labels: The labels to be updated.
    :param new_data: The new data to be displayed.
    """
    if has_display_data_changed(new_data):
        for i, label in enumerate(labels):
            try:
                display.updateLabelText(label, new_data[i])
            except IndexError:
                display.updateLabelText(label, "")


def flood_detection_menu(display, labels):
    """
    Displays the flood detection menu.

    :param display: The display object.
    :param labels: The labels to be updated.
    """
    global info

    info["in_options"] = False

    # Non-functional due to a lack of relevant sensors
    # Flood risk APIs are not usable due to cost

    new_data = ["Flood Detection", "Overall Risk: Low", "Water Levels: 0%", ""]
    push_display_data_changed(display, labels, new_data)


def fire_detection_menu(display, labels):
    """
    Displays the fire detection menu.

    :param display: The display object.
    :param labels: The labels to be updated.
    """
    global info

    info["in_options"] = False

    new_data = ["Fire Detection", f"Overall Risk: {local_temp.fire_risk()}", f"Temperature: {local_temp.local_temp}°C",
                f"Humidity: {local_temp.local_humidity}%"]
    push_display_data_changed(display, labels, new_data)


def warnings_menu(display, labels):
    """
    Displays the warnings menu.

    :param display: The display object.
    :param labels: The labels to be updated.
    """
    global info

    info["in_options"] = False

    new_data = ["Warnings", "No Warnings", "", ""]
    push_display_data_changed(display, labels, new_data)


def motion_detection_menu(display, labels):
    """
    Displays the motion detection menu.

    :param display: The display object.
    :param labels: The labels to be updated.
    """
    global info

    info["in_options"] = False
    new_data = None

    display.updateLabelText(labels[0], "Motion Detection")
    if master.config_dict["motion_enabled"]:
        if motion_detection.motion_detected:
            new_data = ["Motion Detection", "Motion Detected!", "", ""]
        else:
            new_data = ["Motion Detection", "No Motion Detected", "", ""]
    else:
        new_data = ["Motion Detection", "Option Disabled.", "", ""]

    push_display_data_changed(display, labels, new_data)


def select_menu(display, labels, menu, menus):
    highlights_index = menus.index(display_visible_highlights)

    if settings["loop"]:
        if info["display_selector_option"] == highlights_index:
            if (info["last_visible_highlights"] != menu.get_current_list or
                    info["last_selection_option"] != info["display_selector_option"]):
                display_visible_highlights(
                    display, menu, labels)
        else:
            menus[info["display_selector_option"]](display, labels)
        info["last_selection_option"] = info["display_selector_option"]


async def display_menus(display, menu, labels):
    """
    Continuously displays the selected menu.

    :param display: The display object.
    :param menu: The menu object.
    :param labels: The labels to be updated.
    """
    global info

    menus = [motion_detection_menu, warnings_menu,
             flood_detection_menu, fire_detection_menu, display_visible_highlights]

    while True:
        select_menu(display, labels, menu, menus)
        await asyncio.sleep(SLEEP_TIME)


def get_selection_confirm_text(var):
    """
    Gets the confirmation message for a variable change.

    :param var: The variable that has been changed.
    :return: The confirmation message.
    """
    if var:
        return "Option is now True"
    return "Option is now False"


def update_selection_confirm_change(menu, text, display, labels):
    """
    Updates the display with the confirmation message.

    :param menu: The menu object.
    :param text: The confirmation message.
    :param display: The display object.
    :param labels: The labels to be updated.
    """
    selection_index = menu.get_visible_options().index(menu.current_highlighted)

    for i, label in enumerate(labels[1:]):  # Skip the title label
        if i == selection_index:
            display.updateLabelText(label, text)


async def selection_confirm_change(var, menu, display, labels):
    """
    Confirms the change of a variable and updates the display.

    :param var: The variable that has been changed.
    :param menu: The menu object.
    :param display: The display object.
    :param labels: The labels to be updated.
    """
    global settings

    settings["loop"] = False

    text = get_selection_confirm_text(var)
    update_selection_confirm_change(menu, text, display, labels)

    await asyncio.sleep(0.5)
    settings["loop"] = True


def pause_display(display, labels, text="Paused"):
    """
    Pauses the display with a specified message.
    Used when timed functions are outgoing, such as motion detection re-initialisation.

    :param display: The display object.
    :param labels: The labels to be updated.
    :param text: The text to be displayed when the display is paused.
    """
    global settings

    settings["loop"] = False
    display.updateLabelText(labels[0], "")
    display.updateLabelText(labels[1], "Display Paused")
    display.updateLabelText(labels[2], text)
    display.updateLabelText(labels[3], "")


async def toggle_var_and_confirm(var, menu, display, labels):
    """
    Toggles a variable, confirms the change (incl. publishing to Adafruit), and updates the display.

    :param var: The variable to be toggled.
    :param menu: The menu object.
    :param display: The display object.
    :param labels: The labels to be updated.
    """
    master.toggle_var(var)
    networking.publ_data(networking.mqtt_link, var,
                         master.adafruit_conversion_dict[master.config_dict[var]], True)
    await selection_confirm_change(master.config_dict[var], menu,
                                   display, labels)
    master.write_config()
    await asyncio.sleep(SLEEP_TIME)


async def motion_reinitialise(display, labels):
    """
    Re-initialises the motion detection and updates the display.

    :param display: The display object.
    :param labels: The labels to be updated.
    """
    global settings

    pause_display(display, labels, "Re-initialising...")
    master.config_dict["motion_enabled"] = False
    baseline = await asyncio.create_task(motion_detection.get_baseline(5))
    motion_detection.expected_range_cm = (baseline - baseline / 10)
    master.config_dict["motion_enabled"] = True
    settings["loop"] = True


async def process_selection(display, menu, labels):
    global info, settings

    highlight_id_to_function = {
        "motion_re-initialise": motion_reinitialise,
        # Add other mappings here
    }

    if info["cycle_highlighted"]:
        info["cycle_highlighted"] = False
        menu.cycle_highlighted()

    if info["selection_changed"]:
        info["selection_changed"] = False

        highlight_id = menu.current_option + "_" + menu.current_highlighted

        if menu.current_highlighted == "back":
            # Go back to main menu
            menu.set_current_option("main")

        elif highlight_id in highlight_id_to_function:
            # If the current highlight is a function, call it
            await highlight_id_to_function[highlight_id](display, labels)

        elif highlight_id in master.config_dict:
            # If the current highlight is a toggleable option, toggle it
            await toggle_var_and_confirm(highlight_id,
                                         menu, display, labels)

        elif menu.current_highlighted in menu.option_to_defaults["main"]:
            # If in main menu, select the option currently highlighted
            menu.select_current_highlighted()
        else:
            # Catch-all to send user back to main menu
            menu.set_current_option("main")

    if info["exit_program"]:
        settings["loop"] = False
        display.clearScreen()
        await asyncio.sleep(0.5)  # Wait for the display to clear
        display.closeDisplay()
        await asyncio.sleep(0.5)  # Wait for the display to close


async def respond_to_buttons(display, menu, labels):
    global settings

    while True:
        if settings["loop"]:
            await process_selection(display, menu, labels)
        await asyncio.sleep(SLEEP_TIME)


def set_title_text(display, title, menu):
    """
    Displays the current menu and the number of options in the menu

    :param display: The display object.
    :param title: The title label.
    :param menu: The menu object.
    """
    menu_title = display_class.capitalise_first(menu.current_option)
    menu_title = f"{menu_title} Menu {menu.highlighted_index + 1}/{len(menu.option_to_defaults[menu.current_option])}"

    display.updateLabelText(title, menu_title)


def update_display_labels(display, labels, to_display):
    """
    Updates the display labels with the provided text.

    :param display: The display object.
    :param labels: The labels to be updated.
    :param to_display: The text to be displayed.
    """
    for i, label in enumerate(labels[1:]):  # Skip the title label
        try:
            display.updateLabelText(label, to_display[i])
        except IndexError:
            display.updateLabelText(label, "")


def display_visible_highlights(display, menu, labels):
    """
    Displays the currently visible options ("highlights") on the display.

    :param display: The display object.
    :param menu: The menu object.
    :param labels: The labels to be updated.
    """
    global info

    info["in_options"] = True

    to_display = menu.get_current_list()
    set_title_text(display, labels[0], menu)
    update_display_labels(display, labels, to_display)

    info["last_visible_highlights"] = to_display


def configure_display():
    """
    Configures the display.

    :return: The display object and associated labels.
    """
    display = grove_display.BitmapDisplay(1)

    title = display.addLabel(8, 0, 1, "")
    label_1 = display.addLabel(8, 15, 1, "")
    label_2 = display.addLabel(8, 30, 1, "")
    label_3 = display.addLabel(8, 45, 1, "")

    return display, title, label_1, label_2, label_3


async def main():
    """
    The main function that runs the display and responds to button presses.
    """
    menu = display_class.VisibleMenu()

    display, title, label_1, label_2, label_3 = configure_display()
    labels = [title, label_1, label_2, label_3]
    tasks = [display_menus(display, menu, labels),
             respond_to_buttons(display, menu, labels)]

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())

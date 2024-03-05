import asyncio
from Unit19Modules.monochromeDisplay import grove_display

from pico_security_hub.controllers import display_class
from pico_security_hub.sensors import motion_detection
from pico_security_hub.sensors import local_temp
from pico_security_hub.config import networking
from pico_security_hub.config import configuration

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
    "last_visible_highlights": 0,
    "last_selection_option": 0,
}


def has_display_data_changed(new_data: list[str], previous_data: str) -> bool:
    global info
    if new_data != info[previous_data]:
        info[previous_data] = new_data
        return True
    return False


def push_display_data_changed(display, labels, new_data) -> None:
    if not has_display_data_changed(new_data, "previous_data"):
        return

    for i, label in enumerate(labels):
        try:
            display.updateLabelText(label, new_data[i])
        except IndexError:
            display.updateLabelText(label, "")


def display_non_options_menu(display, labels, to_display: list[str]) -> None:
    global info
    info["in_options"] = False

    push_display_data_changed(display, labels, to_display)


def flood_detection_menu(display, labels) -> None:
    new_data = ["Flood Detection", "Overall Risk: Low", "Water Levels: 0%", ""]
    display_non_options_menu(display, labels, new_data)


def fire_detection_menu(display, labels) -> None:
    new_data = ["Fire Detection", f"Overall Risk: {local_temp.fire_risk()}", f"Temperature: {local_temp.local_temp}°C",
                f"Humidity: {local_temp.local_humidity}%"]
    display_non_options_menu(display, labels, new_data)


def warnings_menu(display, labels) -> None:
    new_data = ["Warnings", "No Warnings", "", ""]
    display_non_options_menu(display, labels, new_data)


def motion_detection_menu(display, labels) -> None:
    new_data = ["", "", "", ""]

    display.updateLabelText(labels[0], "Motion Detection")
    if configuration.config_manager.config_dict["motion_enabled"]:
        if motion_detection.motion_detected:
            new_data = ["Motion Detection", "Motion Detected!", "", ""]
        else:
            new_data = ["Motion Detection", "No Motion Detected", "", ""]
    else:
        new_data = ["Motion Detection", "Option Disabled.", "", ""]
    display_non_options_menu(display, labels, new_data)


def select_menu(display, labels, menu, menus) -> None:
    if not settings["loop"]:
        return

    highlights_index = menus.index(display_visible_highlights)

    if info["display_selector_option"] != highlights_index:
        menus[info["display_selector_option"]](display, labels)
        return

    if (info["last_visible_highlights"] != menu.get_current_list()
            or info["last_selection_option"] != info["display_selector_option"]):
        display_visible_highlights(display, menu, labels)
        info["last_selection_option"] = info["display_selector_option"]
        return


async def display_menus(display, menu, labels) -> None:
    global info

    menus = [motion_detection_menu, warnings_menu,
             flood_detection_menu, fire_detection_menu, display_visible_highlights]

    while True:
        select_menu(display, labels, menu, menus)
        await asyncio.sleep(SLEEP_TIME)


def get_selection_confirm_text(var) -> str:
    if var:
        return "Option is now True"
    return "Option is now False"


def update_selection_confirm_change(menu, text, display, labels) -> None:
    selection_index = menu.get_visible_options().index(menu.current_highlighted)

    for i, label in enumerate(labels[1:]):  # Skip the title label
        if i == selection_index:
            display.updateLabelText(label, text)


async def selection_confirm_change(var, menu, display, labels) -> None:
    global settings

    settings["loop"] = False

    text = get_selection_confirm_text(var)
    update_selection_confirm_change(menu, text, display, labels)

    await asyncio.sleep(0.5)
    settings["loop"] = True


def pause_display(display, labels, text="Paused") -> None:
    """
    Pauses the display with a specified message.
    Used when timed functions are outgoing, such as motion detection re-initialisation.
    """
    global settings

    settings["loop"] = False
    display.updateLabelText(labels[0], "")
    display.updateLabelText(labels[1], "Display Paused")
    display.updateLabelText(labels[2], text)
    display.updateLabelText(labels[3], "")


async def toggle_var_and_confirm(var, menu, display, labels) -> None:
    """
    Toggles a variable, confirms the change (incl. publishing to Adafruit), and updates the display.
    """
    configuration.config_manager.toggle_var(var)
    if configuration.config_manager.NETWORKING_ENABLED:
        networking.publ_data(networking.mqtt_link, var,
                             configuration.config_manager.ADAFRUIT_CONVERSION_DICT[
                                 configuration.config_manager.config_dict[var]], True)
    await selection_confirm_change(configuration.config_manager.config_dict[var], menu,
                                   display, labels)
    configuration.config_manager.write_config()
    await asyncio.sleep(SLEEP_TIME)


async def motion_reinitialise(display, labels) -> None:
    global settings

    pause_display(display, labels, "Re-initialising...")
    configuration.config_manager.config_dict["motion_enabled"] = False
    baseline = await asyncio.create_task(motion_detection.get_baseline(5))
    motion_detection.expected_range_cm = (baseline - baseline / 10)
    configuration.config_manager.config_dict["motion_enabled"] = True
    settings["loop"] = True


async def check_for_exit_program(display) -> None:
    if info["exit_program"]:
        settings["loop"] = False
        display.clearScreen()
        await asyncio.sleep(0.5)  # Wait for the display to clear
        display.closeDisplay()
        await asyncio.sleep(0.5)  # Wait for the display to close


async def check_for_selection_changed(display, labels, menu, highlight_id_to_func: dict) -> None:
    global info

    if info["selection_changed"]:
        info["selection_changed"] = False

        highlight_id = menu.current_option + "_" + menu.current_highlighted

        if menu.current_highlighted == "back":
            # Go back to main menu
            menu.set_current_option("main")

        elif highlight_id in highlight_id_to_func:
            # If the current highlight is a function, call it
            await highlight_id_to_func[highlight_id](display, labels)

        elif highlight_id in configuration.config_manager.config_dict:
            # If the current highlight is a toggleable option, toggle it
            await toggle_var_and_confirm(highlight_id,
                                         menu, display, labels)

        elif menu.current_highlighted in menu.option_to_defaults["main"]:
            # If in main menu, select the option currently highlighted
            menu.select_current_highlighted()
        else:
            # Catch-all to send user back to main menu
            menu.set_current_option("main")


def get_highlight_to_func() -> dict:
    return {
        "motion_re-initialise": motion_reinitialise,
        "main_quit": lambda: info.update({"exit_program": True}),
        # Add other mappings here
    }


def check_for_cycle_highlighted(menu: display_class.VisibleMenu) -> bool:
    if info["cycle_highlighted"]:
        info["cycle_highlighted"] = False
        menu.cycle_highlighted()
        return True
    return False


async def process_selection(display, menu, labels) -> None:
    global info, settings

    highlight_id_to_func = get_highlight_to_func()

    check_for_cycle_highlighted(menu)
    await check_for_selection_changed(display, labels, menu, highlight_id_to_func)
    await check_for_exit_program(display)


async def respond_to_buttons(display, menu, labels) -> None:
    while True:
        if settings["loop"]:
            await process_selection(display, menu, labels)
        await asyncio.sleep(SLEEP_TIME)


def set_title_text(display, title, menu) -> None:
    menu_title = display_class.capitalise_first(menu.current_option)
    menu_title = f"{menu_title} Menu {menu.highlighted_index + 1}/{len(menu.option_to_defaults[menu.current_option])}"

    display.updateLabelText(title, menu_title)


def update_labels_with_text(display, labels, to_display) -> None:
    for i, label in enumerate(labels[1:]):  # Skip the title label
        try:
            display.updateLabelText(label, to_display[i])
        except IndexError:
            display.updateLabelText(label, "")


def display_visible_highlights(display, menu, labels) -> None:
    global info

    info["in_options"] = True

    to_display = menu.get_current_list()
    if has_display_data_changed(to_display, "last_visible_highlights"):
        set_title_text(display, labels[0], menu)
        update_labels_with_text(display, labels, to_display)


def configure_display() -> tuple:
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

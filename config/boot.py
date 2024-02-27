import time

from Unit19Modules.neopixel import board_neoPixel as neopixel
from Unit19Modules.monochromeDisplay import grove_display
from pico_security_hub.config import networking
from pico_security_hub.controllers import control_led


def get_skull_lines():
    """
    Returns a list of strings representing a skull image.
    """
    scary_skull = """
      _____
     /     \\
    | ()_() |
    |   ^   |
     \\     /
      \\___/
    """
    return scary_skull.strip().split('\n')


def display_welcome_text(display, t_label, s_label, repeat=4, pause=0.05):
    """
    Displays a welcome text animation on the given display.

    Parameters:
    display (grove_display.BitmapDisplay): The display to use.
    t_label (grove_display.Label): The label to use for the title.
    s_label (grove_display.Label): The label to use for the subtitle.
    repeat (int): The number of times to repeat the animation.
    pause (float): The pause between each animation frame.
    """
    for x in range(4):
        display.updateLabelText(t_label, "WELCOME")
        time.sleep(pause)
        display.updateLabelText(t_label, "W$LCOME")
        time.sleep(pause)
        display.updateLabelText(t_label, "W$LCO&E")
        time.sleep(pause)
        display.updateLabelText(t_label, "W$L%O&E")
        time.sleep(pause)
        display.updateLabelText(t_label, "£$L%O&E")
        time.sleep(pause)
        display.updateLabelText(t_label, "£$L%O&£")
        time.sleep(pause)
        display.updateLabelText(t_label, "£$L%*&£")
        time.sleep(pause)
        display.updateLabelText(t_label, "£$!%*&£")
        time.sleep(pause)
    time.sleep(0.15)

    display.updateLabelText(t_label, "WELCOME")
    display.updateLabelText(s_label, "Initialising Network")


def end_components(display):
    """
    Ends the display components.

    Parameters:
    display (grove_display.BitmapDisplay): The display to use.
    """
    time.sleep(0.25)
    display.clearScreen()
    time.sleep(0.25)
    display.closeDisplay()


def main():
    """
    Main function to start the system.
    """
    display = grove_display.BitmapDisplay(1)
    title = display.addLabel(23, 25, 2, "")
    label_1 = display.addLabel(8, 44, 1, "")
    control_led.neo.setBlue(20)

    y = 0
    skull_dis = [display.addLabel(0, y + i * 10, 1, line) for i, line in enumerate(get_skull_lines())]

    time.sleep(0.1)

    for x in skull_dis:
        display.updateLabelText(x, "")

    display_welcome_text(display, title, label_1)

    status_message = "Connection Success"
    try:
        networking.main()
        control_led.neo.setGreen(20)
    except AttributeError:
        status_message = "Network Connection Failed"
        control_led.neo.setRed(20)
        raise RuntimeError

    display.updateLabelText(label_1, status_message)
    print(status_message)
    end_components(display)


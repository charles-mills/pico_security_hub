import time

from Unit19Modules.neopixel import board_neoPixel as neopixel
from Unit19Modules.monochromeDisplay import grove_display
from pico_security_hub.config import networking


def get_skull_lines():
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


def end_components(display, neopixel):
    time.sleep(0.25)
    display.clearScreen()
    time.sleep(0.25)
    display.closeDisplay()
    neopixel.close()


def main():
    display = grove_display.BitmapDisplay(1)
    neo = neopixel.neoPixel()

    title = display.addLabel(23, 25, 2, "")
    label_1 = display.addLabel(8, 44, 1, "")
    neo.setBlue(20)
    
    y = 0

    for line in get_skull_lines():
        display.addLabel(0, y, 1, line)
        y += 10

    time.sleep(0.1)
    display_welcome_text(display, title, label_1)
    
    try:
        networking.main()
        neo.setGreen(20)
        display.updateLabelText(label_1, "Connection Success")
    except AttributeError:
        print("Network Connection Failed")
        neo.setRed(20)
        display.updateLabelText(label_1, "Connection Failed")
        time.sleep(0.75)
        
    end_components(display, neo)


if __name__ == "__main__":
    main()
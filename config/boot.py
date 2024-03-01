import time

from Unit19Modules.monochromeDisplay import grove_display
from pico_security_hub.config import networking
from pico_security_hub.controllers import control_led

# Constants
DISPLAY_ADDRESS = 1
TITLE_LABEL_X = 23
TITLE_LABEL_Y = 25
TITLE_LABEL_SIZE = 2
SUB_LABEL_X = 8
SUB_LABEL_Y = 44
SUB_LABEL_SIZE = 1
LED_INTENSITY = 20
SLEEP_TIME = 0.1
WELCOME_TEXTS = ["WELCOME", "W$LCOME", "W$LCO&E", "W$L%O&E",
                 "£$L%O&E", "£$L%O&£", "£$L%*&£", "£$!%*&£"]


def get_skull_image_lines():
    scary_skull = """
      _____
     /     \\
    | ()_() |
    |   ^   |
     \\     /
      \\___/
    """
    return scary_skull.strip().split('\n')


class BootSystem:
    def __init__(self):
        self.display = grove_display.BitmapDisplay(DISPLAY_ADDRESS)
        self.title = self.display.addLabel(
            TITLE_LABEL_X, TITLE_LABEL_Y, TITLE_LABEL_SIZE, "")
        self.label_1 = self.display.addLabel(
            SUB_LABEL_X, SUB_LABEL_Y, SUB_LABEL_SIZE, "")
        control_led.neo.setBlue(LED_INTENSITY)

    def update_display_text(self, label, text, pause=SLEEP_TIME):
        """Updates the display text and sleeps for a specified duration."""
        self.display.updateLabelText(label, text)
        time.sleep(pause)

    def display_welcome_animation(self, repeat=4):
        """Displays a welcome animation on the display."""
        for _ in range(repeat):
            for text in WELCOME_TEXTS:
                self.update_display_text(self.title, text)
        self.update_display_text(self.title, "WELCOME")
        self.update_display_text(self.label_1, "Initialising Network")

    def shutdown_display_components(self):
        """Shuts down the display components."""
        self.update_display_text(None, None, 0.25)
        self.display.clearScreen()
        self.update_display_text(None, None, 0.25)
        self.display.closeDisplay()

    def start_system(self):
        """Starts the system."""
        y = 0
        skull_dis = [self.display.addLabel(0, y + i * 10, 1, line)
                     for i, line in enumerate(get_skull_image_lines())]

        self.update_display_text(None, None, SLEEP_TIME)

        for x in skull_dis:
            self.update_display_text(x, "")

        self.display_welcome_animation()

        status_message = "Connection Success"
        try:
            networking.main()
            control_led.neo.setGreen(LED_INTENSITY)
        except Exception as e:
            status_message = f"Network Connection Failed: {e}"
            control_led.neo.setRed(LED_INTENSITY)
            raise RuntimeError(status_message)
        self.update_display_text(self.label_1, status_message)
        print(status_message)
        self.shutdown_display_components()


def main():
    boot_system = BootSystem()
    boot_system.start_system()


if __name__ == "__main__":
    main()

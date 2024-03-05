import time

from Unit19Modules.monochromeDisplay import grove_display
from pico_security_hub.networking import mqtt_handler
from pico_security_hub.controllers import control_led
from pico_security_hub.boot.boot_config import (DISPLAY_ADDRESS, VER_LABEL_X_Y_SIZE, TITLE_LABEL_X_Y_SIZE,
                                                SUB_LABEL_X_Y_SIZE, LED_INTENSITY, SLEEP_TIME, WELCOME_TEXTS, VERSION)


def get_skull_image_lines():
    """Returns a list of strings representing a skull image."""
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
        self.ver_label = self.display.addLabel(VER_LABEL_X_Y_SIZE[0], VER_LABEL_X_Y_SIZE[1],
                                               VER_LABEL_X_Y_SIZE[2], "")
        self.title = self.display.addLabel(TITLE_LABEL_X_Y_SIZE[0], TITLE_LABEL_X_Y_SIZE[1],
                                           TITLE_LABEL_X_Y_SIZE[2], "")
        self.label_1 = self.display.addLabel(SUB_LABEL_X_Y_SIZE[0], SUB_LABEL_X_Y_SIZE[1],
                                             SUB_LABEL_X_Y_SIZE[2], "")
        control_led.neo.setBlue(LED_INTENSITY)

    def update_display_text(self, label, text, pause=0.0):
        """Updates the display text and sleeps for a specified duration."""
        self.display.updateLabelText(label, text)
        time.sleep(pause)

    def display_graphic_animation(self, repeat=1):
        """Displays a graphic (currently a skull) animation on the display."""
        for _ in range(repeat):
            y = 0
            skull_dis = [self.display.addLabel(0, y + i * 10, 1, line)
                         for i, line in enumerate(get_skull_image_lines())]

            for x in skull_dis:
                self.update_display_text(x, "")

    def display_welcome_animation(self, repeat=4):
        """Displays a welcome animation on the display."""
        for _ in range(repeat):
            for text in WELCOME_TEXTS:
                self.update_display_text(self.title, text, SLEEP_TIME)
        self.update_display_text(self.title, "WELCOME")
        self.update_display_text(self.label_1, "Initialising Network")

    def shutdown_display_components(self):
        """Shuts down the display components."""
        self.display.clearScreen()
        time.sleep(0.1)
        self.display.closeDisplay()
        time.sleep(0.1)

    def start_system(self):
        """Starts the system, displays the welcome animation and initialises the network connection."""

        self.update_display_text(self.ver_label, f"PSH v{VERSION}")
        self.display_welcome_animation()

        status_message = "Connection Success"
        try:
            mqtt_handler.main()
            control_led.neo.setGreen(LED_INTENSITY)
        except Exception as e:
            status_message = f"Network Connection Failed: {e}"
            control_led.neo.setRed(LED_INTENSITY)
            raise RuntimeError(status_message)
        print(status_message)
        self.shutdown_display_components()


def main():
    boot_system = BootSystem()
    boot_system.start_system()


if __name__ == "__main__":
    main()

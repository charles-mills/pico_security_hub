class VisibleMenu:
    def __init__(self):
        self.current_menu = "settings"
        self.current_option = "main"
        self.current_highlighted = "audio"

        self.main_menu_highlights = ["audio", "motion", "LED", "temperature"]  # Options in main menu
        self.audio_menu_highlights = ["mute", "low", "back"]  # Options in audio menu
        self.motion_menu_highlights = ["enabled", "publish", "back"]  # Options in motion menu
        self.led_menu_highlights = ["enabled", "back"]  # Options in LED menu
        self.temperature_menu_highlights = ["publish", "back"]  # Options in temperature menu

        self.visible_highlights = []
        self.highlighted_index = 0

        self.option_to_defaults = {
            "main": self.main_menu_highlights,
            "audio": self.audio_menu_highlights,
            "motion": self.motion_menu_highlights,
            "LED": self.led_menu_highlights,
            "temperature": self.temperature_menu_highlights
        }

    def add_arrow_to_highlight(self):
        return f"{self.current_highlighted} <"

    def get_current_list(self):
        current_list = []

        for x in self.get_visible_options():
            if x == self.current_highlighted:
                x = self.add_arrow_to_highlight()
            current_list.append(capitalise_first(x))

        return current_list

    def set_current_menu(self, menu):
        self.current_menu = menu

    def set_current_option(self, option):
        self.current_option = option

    def set_current_highlighted(self, highlighted):
        self.current_highlighted = highlighted
        self.highlighted_index = self.option_to_defaults[self.current_option].index(highlighted)

    def get_visible_options(self):
        # scroll through defaults with a max of 3 visible at once

        maximum_visible = 3

        if self.highlighted_index >= 3:
            return self.option_to_defaults[self.current_option][3::]

        return self.option_to_defaults[self.current_option][:maximum_visible]

    def cycle_highlighted(self):
        try:
            self.highlighted_index = self.option_to_defaults[self.current_option].index(self.current_highlighted)

            if self.highlighted_index + 1 >= len(self.option_to_defaults[self.current_option]):
                self.highlighted_index = 0
            else:
                self.highlighted_index += 1
        except IndexError:
            self.highlighted_index = 0

        self.current_highlighted = self.option_to_defaults[self.current_option][self.highlighted_index]


def capitalise_first(string):
    return string[:1].upper() + string[1:]

class VisibleMenu:
    def __init__(self):
        self.current_menu = "settings"
        self.current_option = "main"
        self.current_highlighted = "audio"

        self.visible_highlights = []
        self.highlighted_index = 0

        self.option_to_defaults = {
            "main": ["audio", "motion", "LED", "adafruit", "quit"],
            "audio": ["mute", "low", "back"],
            "motion": ["enabled", "publish", "re-initialise", "sensitive", "back"],
            "LED": ["enabled", "back"],
            "temperature": ["publish", "back"],
            "adafruit": ["enabled", "back"],
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

    def select_current_highlighted(self):
        self.set_current_option(self.current_highlighted)

    def set_current_option(self, option):
        self.current_option = option
        self.set_current_highlighted(
            self.option_to_defaults[self.current_option][0])

    def set_current_highlighted(self, highlighted):
        self.current_highlighted = highlighted
        self.highlighted_index = self.option_to_defaults[self.current_option].index(
            highlighted)

    def get_visible_options(self):
        # scroll through defaults with a max of 3 visible at once

        maximum_visible = 3

        if self.highlighted_index >= 3:
            return self.option_to_defaults[self.current_option][3::]

        return self.option_to_defaults[self.current_option][:maximum_visible]

    def cycle_highlighted(self):
        options = self.option_to_defaults[self.current_option]
        self.highlighted_index = (self.highlighted_index + 1) % len(options)
        self.current_highlighted = options[self.highlighted_index]


def capitalise_first(string):
    return string[:1].upper() + string[1:]

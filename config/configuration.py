import json


class ConfigManager:
    MASTER_LOOP = True
    NETWORKING_ENABLED = True
    DEBUG_MODE = False

    ADAFRUIT_CONVERSION_DICT = {"ON": True, True: "ON", "OFF": False, False: "OFF"}

    def __init__(self):
        self.config_dict = {
            "audio_mute": False,
            "audio_low": False,
            "motion_enabled": True,
            "motion_publish": True,
            "motion_sensitive": False,
            "LED_enabled": True,
            "temperature_publish": True,
        }

    def log(self, message):
        """ Logs a message (i.e. a caught exception) to a file,
         or prints it to the console if debug mode is active. """
        if not self.DEBUG_MODE:
            with open('pico_security_hub/data/log.txt', 'a', encoding='utf-8') as f:
                f.write(message + '\n')
        else:
            print(message)

    def toggle_var(self, var):
        """ Toggles a variable in the configuration dictionary. """
        if var in self.config_dict:
            self.config_dict[var] = not self.config_dict[var]

    def get_vars(self):
        """ Loads the JSON file containing the configuration dictionary in its last saved state. """
        try:
            if not self.DEBUG_MODE:
                with open("pico_security_hub/data/saved_vars.json", "r", encoding='utf-8') as f:
                    self.config_dict = json.load(f)
        except FileNotFoundError:
            self.log("Could not read the configuration file.")

    def write_config(self):
        """ Writes the configuration dictionary to a JSON file. """
        try:
            if not self.DEBUG_MODE:
                with open("pico_security_hub/data/saved_vars.json", "w", encoding='utf-8') as f:
                    json.dump(self.config_dict, f)
        except Exception as e:
            self.log(f"An error occurred while writing the configuration file: {e}")


config_manager = ConfigManager()

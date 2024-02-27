import json

MASTER_LOOP = True
NETWORKING_ENABLED = True


bool_to_str = {True: "ON", False: "OFF"}
str_to_bool = {"ON": True, "OFF": False}

config_dict = {
    "audio_mute": False,
    "audio_low": False,
    "motion_enabled": True,
    "motion_publish": True,
    "motion_sensitive": False,
    "LED_enabled": True,
    "temperature_publish": True,
}


def log(message):
    """
    Function to log messages to the console or the log.txt file.
    Messages are not written to file if networking is enabled as this
    may suggest the file is being run on an external device, preventing
    the file from being written to.

    :param message: The message to be logged.
    """

    if not NETWORKING_ENABLED:
        with open('pico_security_hub/data/log.txt', 'a', encoding='utf-8') as f:
            f.write(message + '\n')
    else:
        print(message)


def toggle_var(var):
    if var in config_dict:
        config_dict[var] = not config_dict[var]


def get_vars():
    global config_dict

    try:
        with open("pico_security_hub/data/saved_vars.json", "r", encoding='utf-8') as f:
            config_dict = json.load(f)
    except (FileNotFoundError, IOError):
        print("Could not read the configuration file.")


def write_config():
    try:
        with open("pico_security_hub/data/saved_vars.json", "w", encoding='utf-8') as f:
            json.dump(config_dict, f)
    except Exception as e:
        print(f"An error occurred while writing the configuration file: {e}")



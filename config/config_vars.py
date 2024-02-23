import json

master_loop = True
networking_enabled = True


bool_to_str = {
    True: "ON",
    False: "OFF"
}


config_dict = {
    "audio_mute": False,
    "audio_low": False,
    "motion_enabled": True,
    "motion_publish": True,
    "motion_sensitive": False,
    "LED_enabled": True,
    "temperature_publish": True,
}


def toggle_var(var):
    config_dict[var] = not config_dict[var]


def get_vars():
    global config_dict

    with open("pico_security_hub/config/saved_vars.json", "r") as f:
        config_dict = json.loads(f.read())


def write_config():
    with open("pico_security_hub/config/saved_vars.json", "w") as f:
        f.write(json.dumps(config_dict))

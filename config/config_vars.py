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

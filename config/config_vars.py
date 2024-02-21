master_loop = True
networking_enabled = False

config_dict = {
    "audio_mute": True,
    "audio_low": False,
    "motion_enabled": True,
    "motion_publish": True,
    "LED_enabled": True,
    "temperature_publish": True,
}


def toggle_var(var):
    config_dict[var] = not config_dict[var]
master_loop = True

# Audio

audio_enabled = True
audio_low = False

# Motion Detection

motion_detection_enabled = True
publ_motion = True

# LED

led_enabled = True

# Temperature

publ_temp = True


def toggle_var(var):
    if var:
        var = False
    else:
        var = True

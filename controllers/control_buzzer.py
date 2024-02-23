import asyncio

from Unit19Modules.piBuzzer import buzzerOut
from pico_security_hub.config import config_vars as master


buzzer = buzzerOut.Buzzer()


queue_tunes = {
    "success": False,
    "fail": False,
    "start": False,
    "alarm": False,
    "scary": False
}


tunes = {
    "success": ["C4", "E4", "G4", "C5"],
    "fail": ["C5", "G4", "E4", "C4"],
    "start": ["C4", "E4", "G4", "C5", "G4", "E4", "C4"],
    "alarm": ["C4", "E4", "G4", "C5", "G4"],
    "scary": ["C4", "0", "E4", "0", "G4", "0", "C5", "0", "G4", "0", "E4", "0", "C4", "0"]
}


async def play_tune(tune):
    volume = 10
    tempo = 4

    if master.config_dict["audio_low"]:
        volume = 2

    if tune == "alarm":
        tempo = 10

    buzzer.play_tune(tunes[tune], 3, volume, tempo)


async def main():
    while True:
        for tune in queue_tunes:
            if queue_tunes[tune] and not master.config_dict["audio_mute"]::
                await play_tune(tune)
                queue_tunes[tune] = False
            elif queue_tunes[tune]:
                queue_tunes[tune] = False
        await asyncio.sleep(0.1)



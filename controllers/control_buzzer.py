import asyncio
from Unit19Modules.piBuzzer import buzzerOut
from pico_security_hub.config import config_vars as master

buzzer = buzzerOut.Buzzer()
queue = []
tunes = {
    "success": {"notes": ["C4", "E4", "G4", "C5"], "volume": 10, "tempo": 4},
    "fail": {"notes": ["C5", "G4", "E4", "C4"], "volume": 10, "tempo": 4},
    "start": {"notes": ["C4", "E4", "G4", "C5", "G4", "E4", "C4"], "volume": 10, "tempo": 4},
    "alarm": {"notes": ["C4", "E4", "G4", "C5", "G4"], "volume": 10, "tempo": 10},
    "scary": {"notes": ["C4", "0", "E4", "0", "G4", "0", "C5", "0", "G4", "0", "E4", "0", "C4", "0"], "volume": 10,
              "tempo": 4}
}


async def play_tune(tune):
    if master.config_dict["audio_low"]:
        tunes[tune]["volume"] = 2

    buzzer.play_tune(tunes[tune]["notes"], 3, tunes[tune]["volume"], tunes[tune]["tempo"])


async def main():
    while True:
        if queue and not master.config_dict["audio_mute"]:
            await play_tune(queue.pop(0))
        elif queue:
            queue.pop(0)
        await asyncio.sleep(0.1)

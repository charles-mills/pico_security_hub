import asyncio

from pico_security_hub.sensors import motion_detection
from pico_security_hub.sensors import local_temp
from pico_security_hub.networking import mqtt_handler

NO_RISK_MESSAGE = "Everything is fine. No need to worry."
POTENTIAL_RISK_MESSAGE = "There is a potential risk. See below for more information."
HIGH_RISK_MESSAGE = "There is a high risk. Please take action immediately."
CRITICAL_RISK_MESSAGE = "There is a critical risk. Please take action immediately."
UNKNOWN_MESSAGE = "I can't seem to see what's happening. Please see below for more information."

NO_RISK_SHORT_MESSAGE = "All good :)"
POTENTIAL_RISK_SHORT_MESSAGE = "Potential risk detected."
HIGH_RISK_SHORT_MESSAGE = "High risk detected."
CRITICAL_RISK_SHORT_MESSAGE = "Critical risk detected."
UNKNOWN_SHORT_MESSAGE = "I can't think"

SLEEP_TIME = 1
SLEEP_TIME_LONG = 5


class ChatBot:
    def __init__(self):
        self.mood: str = "neutral"
        self.message: str = ""
        self.short_message: str = ""

    def __str__(self):
        return self.message

    def update_message_by_conditions(self) -> None:
        score = self.evaluate_conditions()
        if score == 0:
            self.message = NO_RISK_MESSAGE
            self.short_message = NO_RISK_SHORT_MESSAGE
        elif score == 1:
            self.message = POTENTIAL_RISK_MESSAGE
            self.short_message = POTENTIAL_RISK_SHORT_MESSAGE
        elif score == 2:
            self.message = HIGH_RISK_MESSAGE
            self.short_message = HIGH_RISK_SHORT_MESSAGE
        elif score >= 3:
            self.message = CRITICAL_RISK_MESSAGE
            self.short_message = CRITICAL_RISK_SHORT_MESSAGE
        else:
            self.message = UNKNOWN_MESSAGE
            self.short_message = UNKNOWN_SHORT_MESSAGE

    @staticmethod
    def evaluate_conditions() -> int:
        fire_risk: str = local_temp.fire_risk()
        score = 0

        if motion_detection.motion_detected:
            score += 1

        try:
            if local_temp.local_temp > 25:
                score += 1

            if fire_risk == "High":
                score += 2
            elif fire_risk == "Medium":
                score += 1
        except TypeError:
            pass

        return score


def publ_bot_status(chat_bot: ChatBot) -> bool:
    previous_message: str = chat_bot.message
    chat_bot.update_message_by_conditions()

    if previous_message != chat_bot.message:
        mqtt_handler.publ_data(mqtt_handler.mqtt_link,
                               "bot_status", chat_bot.message, mute=True)
        return True
    return False


async def main() -> None:
    chat_bot = ChatBot()
    await asyncio.sleep(SLEEP_TIME_LONG)

    while True:
        if publ_bot_status(chat_bot):
            await asyncio.sleep(SLEEP_TIME_LONG)
            continue
        await asyncio.sleep(SLEEP_TIME)

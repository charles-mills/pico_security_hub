import asyncio

from pico_security_hub.networking import mqtt_handler


async def track_uptime(uptime, delay_seconds: int = 5):
    await asyncio.sleep(delay_seconds)
    uptime += delay_seconds
    return uptime


async def main():
    uptime = 0
    while True:
        mqtt_handler.publ_data(mqtt_handler.mqtt_link,
                               "uptime", f"{uptime}s", mute=True)
        uptime = await track_uptime(uptime)


if __name__ == "__main__":
    asyncio.run(main())

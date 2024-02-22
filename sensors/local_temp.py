import asyncio

from pico_security_hub.config import networking
from pico_security_hub.config import config_vars as master
from Unit19Modules.DHT_Module import DHT11_Module
from pico_security_hub.controllers import control_led

local_temp = 0
local_humidity = 0


def fire_risk():
    # use both local temperature and humidity to calculate fire risk

    if local_temp > 30 > local_humidity:
        return "High"
    elif local_temp > 30 and local_humidity > 30:
        return "Medium"
    else:
        return "Low"


async def publ_local_temp(dht11):
    global local_temp

    while True:
        if master.master_loop and master.config_dict["temperature_publish"]:
            try:
                local_temp = dht11.getTemperature()
                networking.publ_data(networking.mqtt_link, "localTemperature", local_temp, mute=True)
                await control_led.send_colour()
            except:  # Broad exception clause as the expected error ("MQTT") does not support targeted exception
                pass
        await asyncio.sleep(5)


async def publ_local_humidity(dht11):
    global local_humidity

    while True:
        if master.master_loop and master.config_dict["temperature_publish"]:
            try:
                local_humidity = dht11.getHumidity()
                networking.publ_data(networking.mqtt_link, "localHumidity", local_humidity, mute=True)
                await control_led.send_colour()
            except:  # Broad exception clause as the expected error ("MQTT") does not support targeted exception
                pass
        await asyncio.sleep(5)


async def main():
    dht11 = DHT11_Module.TempHumid(4)

    await asyncio.gather(publ_local_temp(dht11), publ_local_humidity(dht11))


if __name__ == "__main__":
    asyncio.run(main())

import asyncio

from pico_security_hub.config import networking
from pico_security_hub.config import configuration
from Unit19Modules.DHT_Module import DHT11_Module
from pico_security_hub.controllers import control_led

local_temp = 0
local_humidity = 0


def fire_risk():
    """
    Calculate fire risk based on local temperature and humidity.
    Returns a string indicating the level of fire risk.

    Currently non-functional due to a lack of relevant sensors.
    """
    if local_temp > 30 > local_humidity:
        return "High"
    elif local_temp > 30 and local_humidity > 30:
        return "Medium"
    else:
        return "Low"


async def publ_local_data(dht11):
    """
    Publish local temperature and humidity data.
    Updates the global variables local_temp and local_humidity.

    :param dht11: DHT11_Module.TempHumid
    """
    global local_temp
    global local_humidity

    while True:
        if (configuration.config_manager.MASTER_LOOP and
                configuration.config_manager.config_dict["temperature_publish"]):
            try:
                local_humidity = dht11.getHumidity()
                local_temp = dht11.getTemperature()
                networking.publ_data(networking.mqtt_link,
                                     "local_humidity", local_temp, mute=True)
                networking.publ_data(networking.mqtt_link,
                                     "local_temperature", local_temp, mute=True)
                await control_led.send_colour()
            # Broad exception clause as the expected error ("MQTT") does not support targeted exception
            except:
                pass
        await asyncio.sleep(5)


async def main():
    """
    Main function to initialize the temperature and humidity sensor and start publishing data.
    """
    temp_humidity_sensor = DHT11_Module.TempHumid(4)
    await asyncio.gather(publ_local_data(temp_humidity_sensor))


if __name__ == "__main__":
    asyncio.run(main())

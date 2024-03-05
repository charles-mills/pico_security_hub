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

    try:
        if local_temp > 30 > local_humidity:
            return "High"
        elif local_temp > 30 and local_humidity > 30:
            return "Medium"
        else:
            return "Low"
    except:
        return "Unknown"


def handle_humidity(dht11, previous_humidity: float):
    global local_humidity

    local_humidity: float = dht11.getHumidity()

    # if previous humidity is more than 5% +/- current humidity, publish the new humidity
    if abs(local_humidity - previous_humidity) >= 5:
        networking.publ_data(networking.mqtt_link,
                             "local_humidity", local_humidity, mute=True)


def handle_local_temp(dht11, previous_temp: float):
    global local_temp

    local_temp: float = dht11.getTemperature()

    # if previous temp is more than 1c +/- current temp, publish the new temp
    if abs(local_temp - previous_temp) >= 1:
        networking.publ_data(networking.mqtt_link,
                             "local_temperature", local_temp, mute=True)


async def publ_local_data(dht11: DHT11_Module.TempHumid) -> None:
    while True:
        if not configuration.config_manager.MASTER_LOOP and configuration.config_manager.config_dict["temperature_publish"]:
            await asyncio.sleep(5)
            continue
        try:
            handle_humidity(dht11, local_humidity)
            handle_local_temp(dht11, local_temp)
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

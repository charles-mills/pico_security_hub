import asyncio

from pico_security_hub.config import networking
from pico_security_hub.config import config_vars as master
from Unit19Modules.DHT_Module import DHT11_Module


async def publ_local_temp(dht11):
    while True:
        if master.master_loop:
            try:
                local_temp = dht11.getTemperature()
                networking.publ_data(networking.mqtt_link, "localTemperature", local_temp, mute=True)
            except:  # Broad exception clause as the expected error ("MQTT") does not support targeted exception
                pass
        await asyncio.sleep(5)


async def publ_local_humidity(dht11):
    while True:
        if master.master_loop:
            try:
                local_humidity = dht11.getHumidity()
                networking.publ_data(networking.mqtt_link, "localHumidity", local_humidity, mute=True)
            except:
                pass

        await asyncio.sleep(5)


async def main():
    dht11 = DHT11_Module.TempHumid(4)

    await asyncio.gather(publ_local_temp(dht11), publ_local_humidity(dht11))


if __name__ == "__main__":
    asyncio.run(main())

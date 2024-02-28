import re

from Unit19Modules.mqtt import mqtt
from Unit19Modules.wifi import wifiConnectClass
from pico_security_hub.config import config_vars as master

mqtt_link = None


def title(string):
    if string:
        return string[0].upper() + string[1:].lower()
    return ""


def list_feeds(mqtt_l):
    feeds = ["\tSubscribed to  : " + feed for feed in mqtt_l.subscriptions]
    print("\t" + "-" * 40)
    print("\n".join(feeds))
    print("\t" + "-" * 40)


def publ_initial_config():
    for key in master.config_dict:
        publ_data(mqtt_link, key, master.adafruit_conversion_dict[master.config_dict[key]], True)


def connect_adafruit(wifi_links, subscription_list):
    try:
        print("\tConnection to Adafruit Requested")

        mqtt_obj = mqtt.Mqtt(
            wifi_links[1], wifi_links[0], subscription_list)
        mqtt_obj.connection()
        print("\tConnection to Adafruit Established")
        return mqtt_obj
    except Exception as e:
        print(f"An error occurred while connecting to Adafruit: {e}")


def publ_data(mqtt_l, publication, value, mute=False):
    mqtt_l.publishData(publication, value)
    if not mute:
        print(f"\tPublished {title(publication)}: {value} to /feeds/{publication}")


def main():
    global mqtt_link

    subscription_list = []

    for key in master.config_dict:
        subscription_list.append("/feeds/" + key)

    wifi_obj = wifiConnectClass.WiFi()
    wifi_links = wifi_obj.connectToWiFi()

    mqtt_link = connect_adafruit(wifi_links, subscription_list)


if __name__ == "__main__":
    main()


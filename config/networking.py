import re

from Unit19Modules.mqtt import mqtt
from Unit19Modules.wifi import wifiConnectClass

mqtt_link = None
wifi_obj = None
wifi_links = None


def title(string):
    string = list(string)
    string[0] = string[0].upper()

    string = "".join(string)

    string = re.sub(r"([A-Z])", r" \1", string).split()
    return string


def list_feeds(mqtt_l):
    feeds = mqtt_l.subscriptions
    print("\t" + "-" * 40)
    for feed in feeds:
        print("\tSubscribed to  : " + feed)
    print("\t" + "-" * 40)


def connect_adafruit(wifi_links, subscription_list):
    print("\tConnection to Adafruit Requested")

    mqtt_obj = mqtt.Mqtt(
        wifi_links[1], wifi_links[0], subscription_list)
    mqtt_obj.connection()
    print("\tConnection to Adafruit Established")
    return mqtt_obj


def publ_data(mqtt_l, publication, value, mute=False):
    mqtt_l.publishData(publication, value)
    if not mute:
        print(f"\tPublished {title(publication)}: " +
              str(value) + " to /feeds/" + publication)


def main():
    global mqtt_link
    global wifi_obj
    global wifi_links

    publication_list = ["coreTemperature", "motionDetected", "motionPublishingStatus", "motionDetectionDisabled",
                        "audioMuted", "audioLow", "ledOff"]

    subscription_list = ["/feeds/motionPublishingStatus", "/feeds/motionDetectionDisabled", "/feeds/audioMuted",
                         "/feeds/audioLow", "/feeds/ledOff"]

    wifi_obj = wifiConnectClass.WiFi()
    wifi_links = wifi_obj.connectToWiFi()

    mqtt_link = connect_adafruit(wifi_links, subscription_list)


if __name__ == "__main__":
    main()

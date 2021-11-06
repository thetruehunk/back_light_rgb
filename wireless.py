import machine
import network
import uasyncio as asyncio
import utime as time
from functions import load_config



def activate():
    config = load_config("config.json")
    try:
        wifi_if = network.WLAN(network.STA_IF)
        if not wifi_if.isconnected():
            print("connecting to network...")
            wifi_if.active(True)
            wifi_if.connect(config["ESSID"], config["PASSWORD"])
            #  Try connect to Access Point
            a = 0
            while not wifi_if.isconnected() and a != 5:
                print(".", end="")
                time.sleep(2)
                a += 1
        # If module cannot connect to WiFi - he's creates personal AP
        if not wifi_if.isconnected():
            wifi_if.disconnect()
            wifi_if.active(False)
            wifi_if = network.WLAN(network.AP_IF)
            wifi_if.active(True)
            wifi_if.config(essid=(config["AP-ESSID"]),
                           authmode=network.AUTH_WPA_WPA2_PSK,
                           password=(config["AP-PASSWORD"]),
                           channel=int(config["CHANNEL"]))
            wifi_if.ifconfig(
                ("10.27.10.1", "255.255.255.0", "10.27.10.1", "10.27.10.1")
            )
        print("network config:", wifi_if.ifconfig())

    except RuntimeError:
        time.sleep(5)
        machine.reset()


async def check_connection():
    while True:
        # получить доступ к обьекту network 
        wifi_if = network.WLAN(network.STA_IF)
        # проверить активно ли подключение
        if not wifi_if.isconnected():
            print("Connection lost")
        else:
            print("Connection active")
        # если подключение активно - пингуем шлюз
        await asyncio.sleep(60)


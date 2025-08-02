#
#
#
import network
import time
import ntptime

SSID = '<set_your_SSID>'
PASSWD = '<set_your_password>'

def setup_WiFi(id, pwd):
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(id, pwd)
    while station.isconnected() == False:
        pass

    print('Connection successful')
    print(station.ifconfig())

setup_WiFi(SSID, PASSWD)

# Synchronize system clock using NTP
# Wait briefly to ensure DNS is ready
time.sleep(1)

# Try synchronizing  system clock by  NTP
try:
    ntptime.settime()
    print("Time synchronized:", time.localtime())
except OSError as e:
    print("NTP sync failed:", e)

#
#
#

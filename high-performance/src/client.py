#
#  client.py  v0.01 (20250622 20:18)
#
#
import time
import ntptime
import json
from machine import Pin, SPI
from umqtt.simple import MQTTClient


# define for STATE
STATE_OPEN = 1
STATE_READY = 2
STATE_GO = 3
STATE_STOP = 4
STATE_REPORT = 5
STATE_CLOSE = 6

BROKER = 'broker.emqx.io'
PORT = 1883
CLIENT_ID = "RPi_1234"
#MQTT_TOPIC = "game_renda/open"
MQTT_TOPIC = "game_renda/#"

state = STATE_CLOSE

def on_message(topic, msg):
   global state
   print("\nReceived message: ", msg , " on topic: " , topic)
   if topic == b'game_renda/close': 
        state = STATE_CLOSE
        np_clear(np)
   elif topic == b'game_renda/open': 
        np[0]=(10,0,0)
        np.write()
        state = STATE_OPEN
   elif topic == b'game_renda/ready': 
        np[1]=(10,0,0)
        np.write()
   elif topic == b'game_renda/go': 
        np[2]=(10,10,10)
        np.write()
        state = STATE_GO
   elif topic == b'game_renda/stop': 
        np[1]=(0,0,00)
        np.write()
        state = STATE_STOP
   elif topic == b'game_renda/report': 
        np[1]=(0,10,0)
        np[12]=(0,10,0)
        np[23]=(0,10,0)
        np.write()
        state = STATE_REPORT
   else:
        print('????')
#
# setup MQTT
#
client = MQTTClient(CLIENT_ID, BROKER, PORT)
client.set_callback(on_message)
client.connect()
client.subscribe(MQTT_TOPIC)

import neopixel
import machine
np = neopixel.NeoPixel(Pin(16), 24)

def np_clear(np):
    for i in range(len(np)):
       np[i]=(0, 0, 0)
    np.write()

np[0]=(4,4,4)
np.write()

np[4]=(0,0,10)
np.write()


if False:
 while True:
  for i in range(24):
   np[i]=(0,0,10)
   np.write()
   time.sleep(0.01)

  for i in range(24):
   np[i]=(0,0,0)
   np.write()
   time.sleep(0.01)


for i in range(15):
   np[i]=(0,0,0)

np[2]=(0,10,0)
np[4]=(0,0,10)
time.sleep(0.5)
np.write()


#np[0]=(0x00, 0x00, 0x08)
#np.write()

while True:
    #client.wait_msg()
    client.check_msg()
    if state == STATE_GO:
        print('!', end='')
        time.sleep(0.01)
    else:
        print('z', end='')
        time.sleep(0.05)
#
#

#!/usr/bin/python3

#
# simple client is only for debug
#

from topic_defs import *
import datetime
import json
import pdb
import time

#
# MQTT Defs
#
import paho.mqtt.client as mqtt 


#
# EMQX
#
MQTT_BROKER = 'broker.emqx.io'
MQTT_PORT = 1883

#
# HIVE MQ
#
#MQTT_BROKER = 'broker.hivemq.com'
#MQTT_PORT = 1883

#
# local mosquitto
#
#MQTT_BROKER = '192.168.10.100'
#MQTT_PORT = 1883



from topic_defs import *

    
def on_connect(client, userdata, flag, rc):
        print("Connected with result code " + str(rc))
        client.subscribe(TOPIC_COMMAND_CHANGE_STATE, qos=1)  
        client.subscribe(TOPIC_GAME_SUMMARY)
 
    
def on_disconnect(client, userdata, rc):
      if  rc != 0:
          print("Unexpected disconnection.")
    
def on_message(client, userdata, msg):
        topic = msg.topic
        payload = msg.payload
        print('------------------')
        #print("Received: ", topic )
        #print("Received: ", topic , '   ' , payload)
    
        if topic == TOPIC_COMMAND_CHANGE_STATE:
                #print(payload)
                payload_str = payload.decode('utf-8')
                payload_dic = json.loads(payload_str)
                print(topic, payload_dic['state'])
        elif topic == TOPIC_GAME_SUMMARY:
                #print(topic, payload)
                pass
        else:
                print('Error unkown topic', topic)


client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

import time
while True:
   time.sleep(1)
   print('.',end='')
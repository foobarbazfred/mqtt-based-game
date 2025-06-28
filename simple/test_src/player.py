#!/usr/bin/python3


#
# controller for MQTT Renda Oh
# PC Sample Version
# v0.04  2025/6/38 refactor, 
#    Extracted FSM components into a separate module
#


import time
import json
import paho.mqtt.client as mqtt 

MQTT_BROKER = 'broker.emqx.io'
MQTT_PORT = 1883

PLAYER_ID = 'rpi_0001'
PLAYER_NICK_NAME = 'rpi_0001'

from topic_defs import *
from fsm import find_match_state
from fsm import switch_to_state


#
# player's procedure
#
def proc_player_ready():
    print('ready')
def proc_player_countdown_to_start_3():
    print('cdts3')
def proc_player_countdown_to_start_2():
    print('cdts2')
def proc_player_countdown_to_start_1():
    print('cdts1')
    print('ready')
def proc_player_start():
    print('start')
def proc_player_countdown_to_stop_3():
    print('cdtp3')
def proc_player_countdown_to_stop_2():
    print('cdtp2')
def proc_player_countdown_to_stop_1():
    print('cdtp1')
def proc_player_stop():
    print('stop')
def proc_player_result():
    print('result')
def proc_player_status_report():
    print('status_report')
    topic = TOPIC_PLAYERS_REPORT
    cmd_seq = 123
    click_count = 456
    message = json.dumps( {
          'command_id': cmd_seq,
          'click_count': click_count,
          'player_id' : PLAYER_ID,
          'player_nick_name' : PLAYER_NICK_NAME
    } )
    print('publish:' , topic, message)
    client.publish(topic, message)

def proc_player_summary():
    print('summary')


FUNCTION_TABLE = {
    'proc_player_ready' : proc_player_ready,
    'proc_player_countdown_to_start_3' : proc_player_countdown_to_start_3 ,
    'proc_player_countdown_to_start_2' : proc_player_countdown_to_start_2 ,
    'proc_player_countdown_to_start_1' : proc_player_countdown_to_start_1 ,
    'proc_player_start' : proc_player_start,
    'proc_player_countdown_to_stop_3' : proc_player_countdown_to_stop_3 ,
    'proc_player_countdown_to_stop_2' : proc_player_countdown_to_stop_2 ,
    'proc_player_countdown_to_stop_1' : proc_player_countdown_to_stop_1 ,
    'proc_player_stop' : proc_player_stop ,
    'proc_player_result' : proc_player_result,
}

def on_connect(client, userdata, flag, rc):
  print("Connected with result code " + str(rc))
  client.subscribe("game_renda/#")  

def on_disconnect(client, userdata, rc):
  if  rc != 0:
    print("Unexpected disconnection.")

def on_message(client, userdata, msg):
   topic = msg.topic
   payload = msg.payload
   print('------------------')
   print("Received: ", topic , '   ' , payload)
   #end_time = time.perf_counter()
   #elapsed_time = end_time - start_time
   #print(f"Elapsed time: {elapsed_time} seconds")
   # check periodic message
   if 'player' in topic:
        pass  # skip if plyer in topic (send by me)
   elif topic == TOPIC_GAME_STATUS_REPORT:
        proc_player_status_report()
   elif topic == TOPIC_GAME_SUMMARY:
        proc_player_summary()
   else:
       matched_state = find_match_state(topic)
       if matched_state is None:
            print('Error! can not find matched state',topic)
       else:
            print('switch to state' , matched_state)
            switch_to_state(matched_state, FUNCTION_TABLE)


client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
 
client.connect(MQTT_BROKER, MQTT_PORT, 60)

#next_state = STATE_READY

last_state_transfer = 0
duration = 0


#
# main function
#
def player_main_loop():
    client.loop_start()
    while True:
        time.sleep(1)


player_main_loop()

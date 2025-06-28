#!/usr/bin/python3

#
# controller sample for MQTT Renda OH
# PC Sample Version
# v0.04  2025/6/38 refactor, 
#    Extracted FSM components into a separate module
#


import time
import json
import paho.mqtt.client as mqtt 

MQTT_BROKER = 'broker.emqx.io'
MQTT_PORT = 1883

PLAYER_ID = 'rpi_0002'
PLAYER_NICK_NAME = 'rpi_0002'

from fsm import STATE_BEHAVIORS
from fsm import STATE_READY

from topic_defs import *

def on_connect(client, userdata, flag, rc):
  print("Connected with result code " + str(rc))
  client.subscribe("game_renda/player/#")  

def on_disconnect(client, userdata, rc):
  if  rc != 0:
    print("Unexpected disconnection.")


def on_message(client, userdata, msg):
   topic = msg.topic
   message = msg.payload
   print("Received: ", topic , '   ' , message)
   #end_time = time.perf_counter()
   #elapsed_time = end_time - start_time
   #print(f"Elapsed time: {elapsed_time} seconds")
   if topic == TOPIC_PLAYERS_REPORT:
       proc_controller_summary(topic, message)
   else:
       print('Error!! unknown topic', topic)

#
#  { <player_id> : { 'click_count' : 123  }, ... ,}
#
player_status = {}

def update_player_status(player_info):
    global player_status
    player_id = player_info['player_id']
    if player_id in player_status:
       player_status[player_id]['click_count'] = player_info['click_count']
    else:
       player_status[player_id] = {
             'player_id' : player_info['player_id'],
             'player_nick_name' : player_info['player_nick_name'],
             'click_count' : player_info['click_count'],
       }

# called when message :
#     TOPIC_GAME_SUMMARY = f'{TOPIC_BASE}/summary'
#
def proc_controller_summary(topic, message):
    global player_status
    print('summary')
    print(topic, message)
    #import pdb
    #pdb.set_trace()
    msg_str = message.decode('utf-8')
    msg_dic = json.loads(msg_str)
    topic = TOPIC_GAME_SUMMARY
    print(msg_dic)
    update_player_status(msg_dic)
    message = json.dumps( player_status)
    print('publish:' , topic, message)
    client.publish(topic, message)


client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
 
client.connect(MQTT_BROKER, MQTT_PORT, 60)




# controller main loop

def controller_main_loop():

    last_state_transfer = 0
    duration = 0
    cmd_seq = 0
    next_state = STATE_READY

    client.loop_start()

    while True:
        print('---periodic: status check---')
        print('publish:' , TOPIC_GAME_STATUS_REPORT)
        topic = TOPIC_GAME_STATUS_REPORT
        message = json.dumps( {'command_id': cmd_seq} )
        client.publish(topic, message)
        cmd_seq += 1
        if (time.time() - last_state_transfer ) <  duration:
            pass
            print('not now state change')
        else:
            if next_state == STATE_READY:
               print('============== new gate ===============')
            print(f'--- state transfer ->({next_state}) --')
            print('next state:', next_state)
            topic = STATE_BEHAVIORS[next_state]['topic']
            message = json.dumps( {'command_id': cmd_seq} )
            print('publish:' , topic, message)
            client.publish(topic, message)
            cmd_seq += 1
            print('exec:' , STATE_BEHAVIORS[next_state]['function'])
            duration = STATE_BEHAVIORS[next_state]['duration']
            print('wait for:' , duration)
            next_state = STATE_BEHAVIORS[next_state]['next_state']
            last_state_transfer = time.time()
        time.sleep(0.5)
    
controller_main_loop()

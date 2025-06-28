#!/usr/bin/python3

#
#
# controller sample for MQTT Renda OH
#
#

import paho.mqtt.client as mqtt 
import json
import time


MQTT_BROKER = 'broker.emqx.io'
MQTT_PORT = 1883

PLAYER_ID = 'rpi_0002'
PLAYER_NICK_NAME = 'rpi_0002'


TOPIC_BASE = 'game_renda'
GAME_DURATIN = 10   # time for click battle

STATE_READY = 0
STATE_COUNTDOWN_TO_START_3 = 1
STATE_COUNTDOWN_TO_START_2 = 2
STATE_COUNTDOWN_TO_START_1 = 3
STATE_START = 4
STATE_COUNTDOWN_TO_STOP_3 = 5
STATE_COUNTDOWN_TO_STOP_2 = 6
STATE_COUNTDOWN_TO_STOP_1 = 7
STATE_STOP = 8
STATE_RESULT = 9

TOPIC_GAME_READY = f'{TOPIC_BASE}/command/ready'
TOPIC_GAME_COUNTDOWN_TO_START_3 = f'{TOPIC_BASE}/command/countdown/start/3'
TOPIC_GAME_COUNTDOWN_TO_START_2 = f'{TOPIC_BASE}/command/countdown/start/2'
TOPIC_GAME_COUNTDOWN_TO_START_1 = f'{TOPIC_BASE}/command/countdown/start/1'
TOPIC_GAME_START = f'{TOPIC_BASE}/command/start'
TOPIC_GAME_COUNTDOWN_TO_STOP_3 = f'{TOPIC_BASE}/command/countdown/stop/3'
TOPIC_GAME_COUNTDOWN_TO_STOP_2 = f'{TOPIC_BASE}/command/countdown/stop/2'
TOPIC_GAME_COUNTDOWN_TO_STOP_1 = f'{TOPIC_BASE}/command/countdown/stop/1'
TOPIC_GAME_STOP = f'{TOPIC_BASE}/command/stop'
TOPIC_GAME_RESULT = f'{TOPIC_BASE}/command/result'

STATE_BEHAVIORS = {

    STATE_READY : {
       'topic' : TOPIC_GAME_READY,
       'function' : 'game_proc_ready',
       'duration' : 3,
       'next_state' : STATE_COUNTDOWN_TO_START_3,
    },

    STATE_COUNTDOWN_TO_START_3 : {
       'topic' : TOPIC_GAME_COUNTDOWN_TO_START_3,
       'function' : 'game_proc_countdown_to_start_3',
       'duration' : 1,
       'next_state' : STATE_COUNTDOWN_TO_START_2,
    },

    STATE_COUNTDOWN_TO_START_2 : {
       'topic' : TOPIC_GAME_COUNTDOWN_TO_START_2,
       'function' : 'game_proc_countdown_to_start_2',
       'duration' : 1,
       'next_state' : STATE_COUNTDOWN_TO_START_1,
    },

    STATE_COUNTDOWN_TO_START_1 : {
       'topic' : TOPIC_GAME_COUNTDOWN_TO_START_1,
       'function' : 'game_proc_countdown_to_start_1',
       'duration' : 1,
       'next_state' : STATE_START,
    },

    STATE_START : {
       'topic' : TOPIC_GAME_START,
       'function' : 'game_proc_start',
       'duration' : GAME_DURATIN  - 3,    # -3 means countdown
       'next_state' : STATE_COUNTDOWN_TO_STOP_3,
    },

    STATE_COUNTDOWN_TO_STOP_3 : {
       'topic' : TOPIC_GAME_COUNTDOWN_TO_STOP_3,
       'function' : 'game_proc_countdown_to_stop_3',
       'duration' : 1,
       'next_state' : STATE_COUNTDOWN_TO_STOP_2,
    },

    STATE_COUNTDOWN_TO_STOP_2 : {
       'topic' : TOPIC_GAME_COUNTDOWN_TO_STOP_2,
       'function' : 'game_proc_countdown_to_stop_2',
       'duration' : 1,
       'next_state' : STATE_COUNTDOWN_TO_STOP_1,
    },

    STATE_COUNTDOWN_TO_STOP_1 : {
       'topic' : TOPIC_GAME_COUNTDOWN_TO_STOP_1,
       'function' : 'game_proc_countdown_to_stop_1',
       'duration' : 1,
       'next_state' : STATE_STOP,
    },

    STATE_STOP : {
       'topic' : TOPIC_GAME_STOP,
       'function' : 'game_proc_stop',
       'duration' : 3,          # wait for collect player's status
       'next_state' : STATE_RESULT,
    },

    STATE_RESULT : {
       'topic' : TOPIC_GAME_RESULT,
       'function' : 'game_proc_result',
       'duration' : 5,
       'next_state' : STATE_READY,
    },

}


#
# Periodic task (request status to players and report summary)
# (exec every 0.5 sec)

# controller -> player
TOPIC_GAME_QUERY = f'{TOPIC_BASE}/command/status_report'

# player -> controller
TOPIC_PLAYERS_REPORT = f'{TOPIC_BASE}/player/report'

# controller -> player
TOPIC_GAME_SUMMARY = f'{TOPIC_BASE}/summary'


import time



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
       game_proc_summary(topic, message)
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
def game_proc_summary(topic, message):
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
client.loop_start()



next_state = STATE_READY

last_state_transfer = 0
duration = 0
cmd_seq = 0

# controller main loop

while True:
    print('---periodic: status check---')
    print('publish:' , TOPIC_GAME_QUERY)
    topic = TOPIC_GAME_QUERY
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

#!/usr/bin/python3


#
# controller for MQTT Renda Oh
#
#


import time
import json
import paho.mqtt.client as mqtt 


MQTT_BROKER = 'broker.emqx.io'
MQTT_PORT = 1883

TOPIC_BASE = 'game_renda'
GAME_DURATIN = 10   # time for click battle

PLAYER_ID = 'rpi_0001'
PLAYER_NICK_NAME = 'rpi_0001'


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
# game_proc_query()
TOPIC_GAME_QUERY = f'{TOPIC_BASE}/command/status_report'


# player -> controller
TOPIC_PLAYERS_REPORT = f'{TOPIC_BASE}/player/report'

# controller -> player
# game_proc_summary()
TOPIC_GAME_SUMMARY = f'{TOPIC_BASE}/summary'


import time

#
# find matched state with topic
#   eg:  topic:  'command/result'
#        return:  STATE_RESULT
#
def find_match_state(topic):
    for state in STATE_BEHAVIORS.keys():
         if topic == STATE_BEHAVIORS[state]['topic']:
               return state
    else:
         return None

current_state = None
def switch_to_state(next_state):
    global current_state
    invoke_function(STATE_BEHAVIORS[next_state]['function'])
    current_state = next_state


def game_proc_ready():
    print('ready')
def game_proc_countdown_to_start_3():
    print('cdts3')
def game_proc_countdown_to_start_2():
    print('cdts2')
def game_proc_countdown_to_start_1():
    print('cdts1')
    print('ready')
def game_proc_start():
    print('start')
def game_proc_countdown_to_stop_3():
    print('cdtp3')
def game_proc_countdown_to_stop_2():
    print('cdtp2')
def game_proc_countdown_to_stop_1():
    print('cdtp1')
def game_proc_stop():
    print('stop')
def game_proc_result():
    print('result')
def game_proc_query():
    print('query')
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
def game_proc_summary():
    print('summary')



FUNCTION_TABLE = {
    'game_proc_ready' : game_proc_ready,
    'game_proc_countdown_to_start_3' : game_proc_countdown_to_start_3 ,
    'game_proc_countdown_to_start_2' : game_proc_countdown_to_start_2 ,
    'game_proc_countdown_to_start_1' : game_proc_countdown_to_start_1 ,
    'game_proc_start' : game_proc_start,
    'game_proc_countdown_to_stop_3' : game_proc_countdown_to_stop_3 ,
    'game_proc_countdown_to_stop_2' : game_proc_countdown_to_stop_2 ,
    'game_proc_countdown_to_stop_1' : game_proc_countdown_to_stop_1 ,
    'game_proc_stop' : game_proc_stop ,
    'game_proc_result' : game_proc_result,
}

def invoke_function(func_name):
    if func_name in FUNCTION_TABLE:
       return FUNCTION_TABLE[func_name]()
    else:
       print('Error unknown function:', func_name)
       return None

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
   elif topic == TOPIC_GAME_QUERY:
        game_proc_query()
   elif topic == TOPIC_GAME_SUMMARY:
        game_proc_summary()
   else:
       matched_state = find_match_state(topic)
       if matched_state is None:
            print('Error! can not find matched state',topic)
       else:
            print('switch to state' , matched_state)
            switch_to_state(matched_state)

client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
 
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

next_state = STATE_READY

last_state_transfer = 0
duration = 0


#
# main function
#
while True:
    time.sleep(1)




#
# controller for MQTT Renda Oh (v0.03 2025/6/28 21:10)
#
# (1) simple protocol
# (2) Table-driven FSM (FINITE STATE MACHINE)
# (3) common design
#

import time
import json
from machine import Pin, SPI
from umqtt.simple import MQTTClient

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
       'function' : 'proc_player_ready',
       'duration' : 3,
       'next_state' : STATE_COUNTDOWN_TO_START_3,
    },

    STATE_COUNTDOWN_TO_START_3 : {
       'topic' : TOPIC_GAME_COUNTDOWN_TO_START_3,
       'function' : 'proc_player_countdown_to_start_3',
       'duration' : 1,
       'next_state' : STATE_COUNTDOWN_TO_START_2,
    },

    STATE_COUNTDOWN_TO_START_2 : {
       'topic' : TOPIC_GAME_COUNTDOWN_TO_START_2,
       'function' : 'proc_player_countdown_to_start_2',
       'duration' : 1,
       'next_state' : STATE_COUNTDOWN_TO_START_1,
    },

    STATE_COUNTDOWN_TO_START_1 : {
       'topic' : TOPIC_GAME_COUNTDOWN_TO_START_1,
       'function' : 'proc_player_countdown_to_start_1',
       'duration' : 1,
       'next_state' : STATE_START,
    },

    STATE_START : {
       'topic' : TOPIC_GAME_START,
       'function' : 'proc_player_start',
       'duration' : GAME_DURATIN  - 3,    # -3 means countdown
       'next_state' : STATE_COUNTDOWN_TO_STOP_3,
    },

    STATE_COUNTDOWN_TO_STOP_3 : {
       'topic' : TOPIC_GAME_COUNTDOWN_TO_STOP_3,
       'function' : 'proc_player_countdown_to_stop_3',
       'duration' : 1,
       'next_state' : STATE_COUNTDOWN_TO_STOP_2,
    },

    STATE_COUNTDOWN_TO_STOP_2 : {
       'topic' : TOPIC_GAME_COUNTDOWN_TO_STOP_2,
       'function' : 'proc_player_countdown_to_stop_2',
       'duration' : 1,
       'next_state' : STATE_COUNTDOWN_TO_STOP_1,
    },

    STATE_COUNTDOWN_TO_STOP_1 : {
       'topic' : TOPIC_GAME_COUNTDOWN_TO_STOP_1,
       'function' : 'proc_player_countdown_to_stop_1',
       'duration' : 1,
       'next_state' : STATE_STOP,
    },

    STATE_STOP : {
       'topic' : TOPIC_GAME_STOP,
       'function' : 'proc_player_stop',
       'duration' : 3,          # wait for collect player's status
       'next_state' : STATE_RESULT,
    },

    STATE_RESULT : {
       'topic' : TOPIC_GAME_RESULT,
       'function' : 'proc_player_result',
       'duration' : 5,
       'next_state' : STATE_READY,
    },

}


#
# Periodic task (request status to players and report summary)
# (exec every 0.5 sec)

# controller -> player
# proc_player_status_report()
TOPIC_GAME_STATUS_REPORT = f'{TOPIC_BASE}/command/status_report'


# player -> controller
TOPIC_PLAYERS_REPORT = f'{TOPIC_BASE}/player/report'

# controller -> player
# ctrl_player_summary()
TOPIC_GAME_SUMMARY = f'{TOPIC_BASE}/summary'




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

def proc_player_ready():
    print('f:ready')

def proc_player_countdown_to_start_3():
    print('f:cdts3')
    play_sound('count_down')
    np_clear(np)
    for i in range(int(len(np)/3*1)):
         np[i]=(4,0,0)
    np.write()

def proc_player_countdown_to_start_2():
    print('f:cdts2')
    play_sound('count_down')
    np_clear(np)
    for i in range(int(len(np)/3*2)):
         np[i]=(4,0,0)
    np.write()

def proc_player_countdown_to_start_1():
    print('f:cdts1')
    print('f:ready')
    play_sound('count_down')
    np_clear(np)
    for i in range(int(len(np)*1)):
         np[i]=(4,0,0)
    np.write()

def proc_player_start():
    print('f:start')
    np_clear(np)
    play_sound('start')
    for i in range(int(len(np))):
         np[i]=(0,0,8)
    np.write()
    time.sleep(0.1)
    for i in range(int(len(np))):
         np[i]=(0,0,0)
    np.write()


def proc_player_countdown_to_stop_3():
    print('f:cdtp3')
    play_sound('count_down')

def proc_player_countdown_to_stop_2():
    print('f:cdtp2')
    play_sound('count_down')

def proc_player_countdown_to_stop_1():
    print('f:cdtp1')
    play_sound('count_down')

def proc_player_stop():
    print('f:stop')
    play_sound('stop')

def proc_player_result():
    print('f:result')
    play_sound('winner')

def proc_player_status_report():
    print('f:status_report')
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

def proc_player_show_summary():
    print('f:show summary')

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

def on_message(topic, msg):
   #topic = msg.topic
   #payload = msg.payload
   print('------------------')
   print("Received: ", topic , '   ' , msg)
   #end_time = time.perf_counter()
   #elapsed_time = end_time - start_time
   #print(f"Elapsed time: {elapsed_time} seconds")
   topic_str = topic.decode('utf-8')

   # check periodic message
   if 'player' in topic_str:
        pass  # skip if plyer in topic (send by me)
   elif topic_str == TOPIC_GAME_STATUS_REPORT:
        proc_player_status_report()
   elif topic_str == TOPIC_GAME_SUMMARY:
        proc_player_show_summary()
   else:
       matched_state = find_match_state(topic_str)
       if matched_state is None:
            print('Error! can not find matched state', topic_str)
       else:
            print('switch to state' , matched_state)
            switch_to_state(matched_state)

#client = mqtt.Client()
#client.on_connect = on_connect
#client.on_disconnect = on_disconnect
#client.on_message = on_message
#client.connect(MQTT_BROKER, MQTT_PORT, 60)
#client.loop_start()


#
# neo pixel
#
import neopixel
import machine
np = neopixel.NeoPixel(Pin(16), 24)

def np_clear(np):
    for i in range(len(np)):
       np[i]=(0, 0, 0)
    np.write()


#
# buzzer
#
from machine import PWM
buzzer = PWM(Pin(17))

def play_sound(type):

    if type == 'count_down':
       buzzer.freq(700)
       buzzer.duty_u16(32768) 
       time.sleep(0.08)
       buzzer.duty_u16(0) 

    elif type == 'start':
       buzzer.freq(1100)
       buzzer.duty_u16(32768) 
       time.sleep(0.08)
       buzzer.duty_u16(0) 

    elif type == 'stop':
       buzzer.freq(1100)
       buzzer.duty_u16(32768) 
       time.sleep(0.08)
       buzzer.duty_u16(0) 

    elif type == 'winner':
       buzzer.freq(780)
       buzzer.duty_u16(32768) 
       time.sleep(0.1)
       buzzer.duty_u16(0) 
       time.sleep(0.1)
       buzzer.freq(1100)
       buzzer.duty_u16(32768) 
       time.sleep(0.2)
       buzzer.duty_u16(0) 

    elif type == 'loser':
       buzzer.freq(150)
       buzzer.duty_u16(32768) 
       time.sleep(0.1)
       buzzer.duty_u16(0) 
       time.sleep(0.1)
       buzzer.duty_u16(32768) 
       time.sleep(0.2)
       buzzer.duty_u16(0) 


#
# setup MQTT
#
client = MQTTClient(PLAYER_ID, MQTT_BROKER, MQTT_PORT)
client.set_callback(on_message)
client.connect()
client.subscribe("game_renda/#")  

def player_main_loop():
    while True:
       client.check_msg()
       print('z',end="")



player_main_loop()


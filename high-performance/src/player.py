#
#  player.py  v0.03 (20250627 2100)
#
#
import time
import ntptime
import json
from machine import Pin, SPI
from umqtt.simple import MQTTClient

#
# 
CONTROLLER_OR_PLAYER = 'player'

# define for STATE
GAME_STATE_NOT_JOINED = 0
GAME_STATE_WAITING = 1
GAME_STATE_RUNNING = 2
GAME_STATE_STOPPED = 3
GAME_STATE_CLOSED = 4

BROKER = 'broker.emqx.io'
PORT = 1883
PLAYER_ID = "RPi_123456"
PLAYER_NICK_NAME = "lark_01"
GAME_ID = "G_12345"
#MQTT_TOPIC = "game_renda/open"
MQTT_TOPIC = "game_renda/#"


#state = GAME_STATE_NOT_JOINED
current_state = GAME_STATE_WAITING

from machine import PWM
buzzer = PWM(Pin(17))

def join_new_session():
    global GAME_ID
    new_game_topic = f'game_renda/{GAME_ID}/#'
    client.subscribe(new_game_topic)
    # request join to controller
    topic = f'game_renda/{GAME_ID}/join'
    message = {
       'game_id': GAME_ID,
       'player_id':PLAYER_ID,
       'player_nickname': PLAYER_NICK_NAME,
    }
    client.publish(topic, json.dumps(message), qos=0)    

def publish_click_report(msg):
    msg_str = msg.decode('utf-8')
    msg_dic = json.loads(msg_str)

    #game_id = msg_dic['game_id']  # adhoc avoid (must encode)
    game_id = GAME_ID
    value = pio_counter.get_counter()
    message = {                      # adhoc
         'game_id' : game_id,            # msg_dic['game_id'],
         'cmd_seq_id' : 1,               # msg_dic['cmd_seq_id'],
         'player_id' : PLAYER_ID,
         'counter' : value,
    }
    topic = f'game_renda/{game_id}/player/{PLAYER_ID}/click_report'
    client.publish(topic, json.dumps(message), qos=0)    


def play_sound(type):
    if type == 'count_down':
       buzzer.freq(700)
       buzzer.duty_u16(32768) 
       time.sleep(0.1)
       buzzer.duty_u16(0) 
       time.sleep(0.1)
       buzzer.duty_u16(32768) 
       time.sleep(0.1)
       buzzer.duty_u16(0) 
       time.sleep(0.1)
       buzzer.duty_u16(32768) 
       time.sleep(0.1)
       buzzer.duty_u16(0) 
       time.sleep(0.1)
       buzzer.freq(1100)
       time.sleep(0.05)
       buzzer.duty_u16(32768) 
       time.sleep(0.1)
       buzzer.duty_u16(0) 
       time.sleep(0.1)


def process_report_topics(topic,msg):
    topic_str = topic.decode('utf-8')
    if 'summary' in topic_str:
        msg_str = msg.decode('utf-8')
        msg_dic = json.loads(msg_str)
        my_clicks = msg_dic['summary'][PLAYER_ID]
        if my_clicks/10 > len(np):
             norm_level = len(np)-1
        else:            
             norm_level = my_clicks / 10
        for i in range(len(np)):
            np[i]=(0,0,0)
        for i in range(norm_level):
            np[i]=(0,0,7)
        np.write()


def process_command_topics(topic, msg):

   global current_state

   # convert bytes to str
   topic_str = topic.decode("utf-8")

   if 'close' in topic_str:
        current_state = GAME_STATE_CLOSED
        np_clear(np)

   elif 'countdown' in topic_str:
        play_sound('count_down')

   elif 'start' in topic_str:
        np[2]=(10,10,10)
        np.write()
        current_state = GAME_STATE_RUNNING
        np_clear(np)
        pio_counter.sm.restart()       # set counter 0

   elif 'stop' in topic_str:
        np[1]=(0,0,00)
        np.write()
        current_state = GAME_STATE_STOPPED

   elif 'poll_clicks' in topic_str:
        publish_click_report(msg)
        np[0]=(0,10,0)
        np[6]=(0,10,0)
        np[12]=(0,10,0)
        np[18]=(0,10,0)
        np.write()

   elif 'close' in topic_str:
        print('close game session')
        current_state = GAME_STATE_STOPPED

   else: 
        print('internal error')
        print('unknown topic:', topic)




#   elif topic_str == 'game_renda/lobby/announce': 
#   elif topic_str == 'game_renda/lobby/response': 
#   topic_str == 'game_renda/lobby/announce': 

zzz = None
def process_message_lobby(topic, msg):

   global GAME_ID
   global zzz
   topic_str = topic.decode("utf-8")
   msg_str = msg.decode("utf-8")
   zzz = msg_str
   msg_dic = json.loads(msg_str)

   if 'lobby/announce' in topic_str or 'lobby/response' in topic_str:
        GAME_ID = msg_dic['game_id']
   else:
        print('Error , unknown topic')
        print(topic)

def on_message(topic, msg):

   global current_state
   global GAME_ID 

   print()
   print('===========================================')
   print('TOPIC: ', topic)
   print('===========================================')
   print('MSG:', msg)
   print('-----------------------------------------')

   # convert bytes to str
   topic_str = topic.decode("utf-8")
   msg_str = msg.decode("utf-8")

   if 'command' in topic_str:
        process_command_topics(topic, msg)

   elif 'player' in topic_str:
         pass                      # skip player's publis

   elif 'lobby' in topic_str:
        process_message_lobby(topic, msg)

   elif topic_str == f'game_renda/{GAME_ID}/join_response':
        msg_dic = json.loads(msg_str)
        if msg_dic['player_id'] == PLAYER_ID:
            game_id = msg_dic['game_id']
            join_game_session(game_id)

   elif 'summary' in topic_str:
        process_report_topics(topic,msg)

   elif 'results' in topic_str:
        process_report_topics(topic,msg)

   else:
        print('Error! unknown topic')
        print(topic_str)

import neopixel
import machine
np = neopixel.NeoPixel(Pin(16), 24)

def np_clear(np):
    for i in range(len(np)):
       np[i]=(0, 0, 0)
    np.write()



# import counter
import pio_counter
pio_counter.sm.restart()       # set counter 0

#loop_counter = 0

last_join_req_time = 0

def main_loop():

    loop_counter = 0
    last_join_req_time = 0
    while True:

        client.check_msg()
        if current_state == GAME_STATE_NOT_JOINED:
            join_new_session()
            last_join_req_time = time.ticks_ms()
        else:
           if current_state == GAME_STATE_RUNNING:
                print('!', end='')
                time.sleep(0.01)
           else:
                print('z', end='')
                time.sleep(0.05)
    
        loop_counter += 1
        if loop_counter > 1000:
            loop_counter = 0
    
#
# setup MQTT
#
client = MQTTClient(PLAYER_ID, BROKER, PORT)
client.set_callback(on_message)
client.connect()
client.subscribe(MQTT_TOPIC)
main_loop()


#
#
#

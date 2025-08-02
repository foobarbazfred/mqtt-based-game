#!/usr/bin/python3

#
# MQTT Renda Oh  (controller.py)
#
# v0.01 (20250627 21:00)

import paho.mqtt.client as mqtt 
import time
import json

BROKER = 'broker.emqx.io'

start_time = 0

GAME_ID = "G_12345"
CONTROLLER_ID = 'RPi_54321'

# define for STATE
GAME_STATE_WAITING = 1
GAME_STATE_COUNTDOWN_TO_START = 2
GAME_STATE_START = 3
GAME_STATE_RUNNING = 4
GAME_STATE_COUNTDOWN_TO_STOP = 5
GAME_STATE_STOP = 6
GAME_STATE_REPORTING = 7
GAME_STATE_CLOSED = 8

next_state = GAME_STATE_WAITING
current_state = None

# define for TOPICS

TOPIC_LIST = {
  'COMMAND_GAME_COUNTDOWN' :  'game_renda/<GAME_ID>/command/countdown',
  'COMMAND_GAME_START' : 'game_renda/<GAME_ID>/command/start',
  'COMMAND_GAME_POLLING' : 'game_renda/<GAME_ID>/command/poll_clicks',
  'COMMAND_GAME_STOP' : 'game_renda/<GAME_ID>/command/stop',
  'COMMAND_GAME_CLOSE' : 'game_renda/<GAME_ID>/command/close',
  'REPORT_GAME_SUMMARY' : 'game_renda/<GAME_ID>/summary',
  'REPORT_GAME_RESULTS' : 'game_renda/<GAME_ID>/results',
  'LOBBY_ANNOUNCE' : 'game_renda/lobby/announce',
  'LOBBY_RESPONSE' : 'game_renda/lobby/response',
}

NEXT_STATE = {
  GAME_STATE_WAITING :  GAME_STATE_COUNTDOWN_TO_START ,
  GAME_STATE_COUNTDOWN_TO_START : GAME_STATE_START ,
  GAME_STATE_START : GAME_STATE_RUNNING  ,
  GAME_STATE_RUNNING : GAME_STATE_COUNTDOWN_TO_STOP ,
  GAME_STATE_COUNTDOWN_TO_STOP : GAME_STATE_STOP ,
  GAME_STATE_STOP : GAME_STATE_REPORTING ,
  GAME_STATE_REPORTING : GAME_STATE_CLOSED, 
  GAME_STATE_CLOSED : None,
}




def on_connect(client, userdata, flag, rc):
  print("Connected with result code " + str(rc))
  client.subscribe("game_renda/#")       # '#' matches multi level  / cf '+'

def on_disconnect(client, userdata, rc):
  if  rc != 0:
    print("Unexpected disconnection.")


player_list = []
count_sum = {}

import pdb
def on_message(client, userdata, msg):
  global count_sum
  received_topic = msg.topic
  received_message = msg.payload

  # skip my message
  if 'command' in str(received_topic):
      return

  print("Received message '" + str(received_message) + "' on topic '" + received_topic)
  end_time = time.perf_counter()
  elapsed_time = end_time - start_time
  print(f"Elapsed time: {elapsed_time} seconds")

  if 'click_report' in received_topic:
       msg_dic = json.loads(received_message)
       player_id = msg_dic['player_id']
       counter = msg_dic['counter']
       count_sum[player_id] = counter
       if current_state == GAME_STATE_RUNNING:
           message = {
                'game_id' : GAME_ID,
                'summary' : count_sum,
           }
           topic = create_topic('REPORT_GAME_SUMMARY')
       elif  current_state == GAME_STATE_REPORTING:
           message = {
                'game_id' : GAME_ID,
                'results' : count_sum,
           }
           topic = create_topic('REPORT_GAME_RESULTS')
       client.publish(topic, json.dumps(message))

  elif 'lobby/request' in received_topic:
     message = {'game_id': GAME_ID, 'game_name' : 'renda oh (12345)'}
     client.publish(TOPIC_LIST['LOBBY_ANNOUNCE'], json.dumps(message))
  else:
     print('Error unknown topic')
     print(received_topic)
      

def create_topic(topic_name):
   #import pdb
   #pdb.set_trace()
   topic = TOPIC_LIST[topic_name].replace('<GAME_ID>',GAME_ID)
   return topic


client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
 
client.connect(BROKER, 1883, 60)
client.loop_start()

i  = 10

print(BROKER)
start_time = time.perf_counter()

wait_time = 2
nth_polling = 0
while True:

    print('next' , next_state)

    if next_state == GAME_STATE_WAITING:
         message = {'game_id': GAME_ID, 'game_name' : 'renda oh (12345)'}
         client.publish(TOPIC_LIST['LOBBY_ANNOUNCE'], json.dumps(message))
         current_state = next_state
         next_state = NEXT_STATE[current_state]
         wait_time = 5

    elif  next_state == GAME_STATE_COUNTDOWN_TO_START:
         topic = create_topic('COMMAND_GAME_COUNTDOWN')
         client.publish(topic, f'hello {i}')
         current_state = next_state
         next_state =  NEXT_STATE[current_state]
         wait_time = 0

    elif  next_state == GAME_STATE_START:
         topic = create_topic('COMMAND_GAME_START')
         client.publish(topic, f'hello {i}')
         current_state = next_state
         next_state =  NEXT_STATE[current_state]
         nth_polling = 0
         wait_time = 1

    elif  next_state == GAME_STATE_RUNNING:
         current_state = next_state
         next_state = None

    elif  next_state == GAME_STATE_COUNTDOWN_TO_STOP:
         topic = create_topic('COMMAND_GAME_COUNTDOWN')
         client.publish(topic, f'hello {i}')
         current_state = next_state
         next_state =  NEXT_STATE[current_state]
         wait_time = 1

    elif  next_state == GAME_STATE_STOP:
         topic = create_topic('COMMAND_GAME_STOP')
         client.publish(topic, f'hello {i}')
         current_state = next_state
         next_state =  NEXT_STATE[current_state]
         wait_time = 1

    elif  next_state == GAME_STATE_REPORTING:
         topic = create_topic('COMMAND_GAME_POLLING')
         message = {'game_id' : GAME_ID, 'cmd_seq_id' : 1}
         client.publish(topic, json.dumps(message))
         current_state = next_state
         next_state =  NEXT_STATE[current_state]
         wait_time = 2

    elif  next_state == GAME_STATE_CLOSED:
         topic = create_topic('COMMAND_GAME_CLOSE')
         client.publish(topic, f'hello {i}')
         current_state = next_state
         next_state =  NEXT_STATE[current_state]
         wait_time = 2

    elif next_state is None:
         print('current' , current_state)
         if current_state == GAME_STATE_RUNNING:
             if nth_polling < 5:      # should be 10
                 topic = create_topic('COMMAND_GAME_POLLING')
                 message = {
                       'game_id' : GAME_ID, 
                       'cmd_seq_id' : 1,
                       'nth_polling' : nth_polling, 
                 }
                 client.publish(topic, json.dumps(message))
                 print('pub:', topic) 
                 next_state = None
                 current_state =  GAME_STATE_RUNNING  # keep current_state
                 nth_polling += 1
             else:
                 next_state = GAME_STATE_COUNTDOWN_TO_STOP
             wait_time = 2

    else:
         print('internal error\n unknwon state,\n so back to GAME_STATE_OPEN')
         next_state = GAME_STATE_OPEN
         wait_time = 0

    time.sleep(wait_time)


client.disconnect()

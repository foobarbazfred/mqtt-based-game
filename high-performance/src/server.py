#!/usr/bin/python3

#
# MQTT Renda King  (MRK)
#

import paho.mqtt.client as mqtt 
import time


BROKER = 'broker.emqx.io'

start_time = 0


# define for STATE
STATE_OPEN = 1
STATE_READY = 2
STATE_GO = 3
STATE_STOP = 4
STATE_REPORT = 5
STATE_CLOSE = 6

current_state = STATE_OPEN


SUBJECT_LIST = {
  STATE_OPEN : 'game_renda/open',
  STATE_READY : 'game_renda/ready',
  STATE_GO :  'game_renda/go',
  STATE_STOP : 'game_renda/stop',
  STATE_REPORT : 'game_renda/report',
  STATE_CLOSE : 'game_renda/close',
}

NEXT_STATE = {
  STATE_OPEN :  STATE_READY ,
  STATE_READY : STATE_GO ,
  STATE_GO : STATE_STOP  ,
  STATE_STOP : STATE_REPORT ,
  STATE_REPORT : STATE_CLOSE, 
  STATE_CLOSE : STATE_OPEN ,
}



def on_connect(client, userdata, flag, rc):
  print("Connected with result code " + str(rc))
  client.subscribe("game_renda/#")       # '#' matches multi level  / cf '+'

def on_disconnect(client, userdata, rc):
  if  rc != 0:
    print("Unexpected disconnection.")

def on_message(client, userdata, msg):
  print("Received message '" + str(msg.payload) + "' on topic '" + msg.topic)
  end_time = time.perf_counter()
  elapsed_time = end_time - start_time
  print(f"Elapsed time: {elapsed_time} seconds")


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
while True:

    print(current_state)

    if current_state == STATE_OPEN:
         client.publish(SUBJECT_LIST[current_state], f'hello {i}')
         current_state = NEXT_STATE[current_state]
         wait_time = 5

    elif  current_state == STATE_READY:
         client.publish(SUBJECT_LIST[current_state], f'hello {i}')
         current_state =  NEXT_STATE[current_state]
         wait_time = 3

    elif  current_state == STATE_GO:
         client.publish(SUBJECT_LIST[current_state], f'hello {i}')
         current_state =  NEXT_STATE[current_state]
         wait_time = 10

    elif  current_state == STATE_STOP:
         client.publish(SUBJECT_LIST[current_state], f'hello {i}')
         current_state =  NEXT_STATE[current_state]
         wait_time = 2

    elif  current_state == STATE_REPORT:
         client.publish(SUBJECT_LIST[current_state], f'hello {i}')
         current_state =  NEXT_STATE[current_state]
         wait_time = 2

    elif  current_state == STATE_CLOSE:
         client.publish(SUBJECT_LIST[current_state], f'hello {i}')
         current_state =  NEXT_STATE[current_state]
         wait_time = 2

    else:
         print('internal error\n unknwon state,\n so back to STATE_OPEN')
         current_state = STATE_OPEN
         wait_time = 0

    time.sleep(wait_time)


client.disconnect()






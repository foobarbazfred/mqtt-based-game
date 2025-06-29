#
# class GameAgent
# micropython version
# manage State Machine and communicate controller and players
#
# v0.07  2025/6/29 17:00
#    create game_agent
# v0.08  2025/6/29 21:00
#    refine functions
#

from topic_defs import *
import json


GAME_DURATIN = 10   # time for click battle

INIT_STATE = 'STATE_OPEN'
current_state = None

# mqtt client

game_id = None

is_controller = False
is_player = False

player_status = {}

def proc_agent_open_game():
    global game_id
    global player_status
    print('open_new_game')
    game_id = 'game_12345'
    player_status = {}

STATE_BEHAVIORS = {

    'STATE_OPEN' : {
       'topic' : TOPIC_COMMAND_CHANGE_STATE,
       'payload' : {'state' : 'STATE_OPEN'},
       'player_action' : None,
       'agent_action' : proc_agent_open_game,
       'duration' : 3,
       'next_state' : 'STATE_READY',
    },

    'STATE_READY' : {
       'topic' : TOPIC_COMMAND_CHANGE_STATE,
       'payload' : {'state' : 'STATE_READY'},
       'player_action' : None,
       'duration' : 3,
       'next_state' : 'STATE_COUNTDOWN_TO_START_3',
    },

    'STATE_COUNTDOWN_TO_START_3' : {
       'topic' : TOPIC_COMMAND_CHANGE_STATE,
       'payload' : {'state' : 'STATE_COUNTDOWN_TO_START_3'},
       'player_action' : None,
       'duration' : 1,
       'next_state' : 'STATE_COUNTDOWN_TO_START_2',
    },

    'STATE_COUNTDOWN_TO_START_2' : {
       'topic' : TOPIC_COMMAND_CHANGE_STATE,
       'payload' : {'state' : 'STATE_COUNTDOWN_TO_START_2'},
       'player_action' : None,
       'duration' : 1,
       'next_state' : 'STATE_COUNTDOWN_TO_START_1',
    },

    'STATE_COUNTDOWN_TO_START_1' : {
       'topic' : TOPIC_COMMAND_CHANGE_STATE,
       'payload' : {'state' : 'STATE_COUNTDOWN_TO_START_1'},
       'player_action' : None,
       'duration' : 1,
       'next_state' : 'STATE_START',
    },

    'STATE_START' : {
       'topic' : TOPIC_COMMAND_CHANGE_STATE,
       'payload' : {'state' : 'STATE_START'},
       'player_action' : None,
       'duration' : GAME_DURATIN  - 3,    # -3 means countdown
       'next_state' : 'STATE_COUNTDOWN_TO_STOP_3',
    },

    'STATE_COUNTDOWN_TO_STOP_3' : {
       'topic' : TOPIC_COMMAND_CHANGE_STATE,
       'payload' : {'state' : 'STATE_COUNTDOWN_TO_STOP_3'},
       'player_action' : None,
       'duration' : 1,
       'next_state' : 'STATE_COUNTDOWN_TO_STOP_2',
    },

    'STATE_COUNTDOWN_TO_STOP_2' : {
       'topic' : TOPIC_COMMAND_CHANGE_STATE,
       'payload' : {'state' : 'STATE_COUNTDOWN_TO_STOP_2'},
       'player_action' : None,
       'duration' : 1,
       'next_state' : 'STATE_COUNTDOWN_TO_STOP_1',
    },

    'STATE_COUNTDOWN_TO_STOP_1' : {
       'topic' : TOPIC_COMMAND_CHANGE_STATE,
       'payload' : {'state' : 'STATE_COUNTDOWN_TO_STOP_1'},
       'player_action' : None,
       'duration' : 1,
       'next_state' : 'STATE_STOP',
    },

    'STATE_STOP' : {
       'topic' : TOPIC_COMMAND_CHANGE_STATE,
       'payload' : {'state' : 'STATE_STOP'},
       'player_action' : None,
       'duration' : 3,          # wait for collect player's status
       'next_state' : 'STATE_RESULT',
    },

    'STATE_RESULT' : {
       'topic' : TOPIC_COMMAND_CHANGE_STATE,
       'payload' : { 'state' : 'STATE_RESULT' , 
                     'player_status' : None,   # set value in  _switch_to_state_for_controller(next_state):
                   },
       'player_action' : None,
       'duration' : 5,
       'next_state' : 'STATE_CLOSE',
    },

    'STATE_CLOSE' : {
       'topic' : TOPIC_COMMAND_CHANGE_STATE,
       'payload' : {'state' : 'STATE_CLOSE'},
       'player_action' : None,
       'duration' : 0,
       'next_state' : None
    },
}


def set_cb_func(state_name,func):
   if state_name in STATE_BEHAVIORS:
       STATE_BEHAVIORS[state_name]['player_action'] = func
   else:
       print('Error in set_cb_func')
       print('unknown state name', state_name)

def init_state():
    switch_to_state(INIT_STATE)    

def get_current_state():
    return current_state

def get_next_state():
    return STATE_BEHAVIORS[current_state]['next_state']

def get_duration_to_transition(state):
    return STATE_BEHAVIORS[state]['duration']

def switch_to_next_state():
    return switch_to_state(get_next_state())

def switch_to_state(next_state):

    if is_controller:
        return _switch_to_state_for_controller(next_state)
    else:
        return _switch_to_state_for_player(next_state)

#
# return current_state
#   topic: str
#   payload: dic
#
def switch_state_by_message(topic, payload):
    if topic != TOPIC_COMMAND_CHANGE_STATE:
       print('Error in switch state by message')
       print('not collect topic', topic)
    state = payload['state']
    if state in STATE_BEHAVIORS:
        switch_to_state(state)
    else: 
       print('Error in switch state')
       print('can not find match topic', topic)
    return current_state


def _exec_agent_action(state):
    if 'agent_action' in STATE_BEHAVIORS[state]:
       func = STATE_BEHAVIORS[state]['agent_action']
       if func is not None:
            func()
#
# state switch function for controller
#
# return value:
#    current_state:  current state name
#    duration:  (wait time until transfer to next state)
#
cmd_seq = 0
def _switch_to_state_for_controller(next_state):
    global cmd_seq
    global current_state

    if not next_state in STATE_BEHAVIORS:
        print('Error ! no match next_state in STATE_BEHAVIORS', state)
        return (current_state, 0)
    else:
        if next_state == 'STATE_READY':
            print('============== READY!!! ===============')

        _exec_agent_action(next_state)
        print(f'--- state transfer ->({next_state}) --')
        print('next state:', next_state)
        topic = STATE_BEHAVIORS[next_state]['topic']
        payload = STATE_BEHAVIORS[next_state]['payload']
        duration = STATE_BEHAVIORS[next_state]['duration']
        payload['cmd_seq'] = cmd_seq
        payload['time_stamp'] = '2000/01/01 00:00:00'
        if next_state == 'STATE_RESULT':
            payload['player_status'] = player_status     
        print('publish:' , topic, payload)
        client.publish(topic, json.dumps(payload))
        cmd_seq += 1
        current_state = next_state
        return  (current_state , duration)

#
#
# state switch function for player
# return: current_state
#
def _switch_to_state_for_player(state):
    global current_state

    if not state in STATE_BEHAVIORS:
        print('Error ! no match next_state in STATE_BEHAVIORS', state)
    else:
        _exec_agent_action(state)
        player_action = STATE_BEHAVIORS[state]['player_action']
        if player_action is None:
             print('not defined function, skip', state)
             val = None
        else:
             val = player_action()
        current_state = state

    return current_state




#
#    { <player_id> : { 'click_count' : 123  }, ... ,}
#  
#



#
# publish game summary  from controller via game_agent 
# controller -----> game_agent  --->  player
#
#
def proc_agent_publish_game_summary():
    topic = TOPIC_GAME_SUMMARY
    payload = {
        'game_id' : game_id,
        'player_status' : player_status,
    }
    client.publish(topic, json.dumps(payload))


#
# periodic topics and function
# publish player -> controller via game_agent
#
#

def proc_agent_status_report(player_id, nick_name, click_count):
    topic = TOPIC_PLAYER_REPORT
    cmd_seq = 123
    message = json.dumps( {
          'command_id': cmd_seq,
          'click_count': click_count,
          'player_id' : player_id,
          'player_nick_name' : nick_name
    } )
    print('publish:' , topic, message)
    client.publish(topic, message)


#def proc_player_summary():
#    print('summary')






#
# received  message (game summary ) from  controller via game_agent
#   game_agent w/controller --->  game_agent w/player
#   topic: str
#   payload: dic
#
def proc_agent_receive_game_summary(topic, payload):
    global player_status
    player_status = payload['player_status']


#
# get report from player then update player status
#   topic : str
#   payload : dic
def proc_agent_receive_player_report(topic, payload):
    global player_status
    player_id = payload['player_id']
    if player_id in player_status:
        player_status[player_id]['click_count'] = payload_dic['click_count']
    else:
        player_status[player_id] = {
            'player_id' : payload['player_id'],
            'player_nick_name' : payload['player_nick_name'],
            'click_count' : payload['click_count'],
        }









# not used
# called when message :
#     TOPIC_GAME_SUMMARY = f'{TOPIC_BASE}/summary'
#
# def proc_summary(topic, message):
#     global player_status
#     print('summary')
#     print(topic, message)
#     msg_str = message.decode('utf-8')       # need this??
#     msg_dic = json.loads(msg_str)
#     topic = TOPIC_GAME_SUMMARY
#     print(msg_dic)
#     update_player_status(msg_dic)
#     message = json.dumps( player_status)
#     print('publish:' , topic, message)
#     client.publish(topic, message)


# main loop for controller 




#
# MQTT Handlers
#

def on_message(topic, msg):
    global current_state
    payload = msg
    print('------------------')
    print("Received: ", topic , '   ' , payload)
    topic_str = topic.decode('utf-8')
    payload_str = payload.decode('utf-8')
    payload_dic = json.loads(payload_str)
    if is_controller:
        if topic_str == TOPIC_PLAYER_REPORT:
            # update player state
            proc_agent_receive_player_report(topic_str, payload_dic)
        else:
            print('Error!! unknown topic(L370)', topic_str)
    else:
        if 'player' in topic_str:
            pass  # skip if plyer in topic (send by me)
        elif topic_str == TOPIC_COMMAND_CHANGE_STATE:
            current_state = switch_state_by_message(topic_str, payload_dic)
        elif topic_str == TOPIC_GAME_SUMMARY:
            proc_agent_receive_game_summary(topic_str, payload_dic)
        else:
            print('Error unkown topic(L370)', topic_str)
        

#
# setup MQTT
#

#import paho.mqtt.client as mqtt 
#client = mqtt.Client()
#client.on_connect = on_connect
#client.on_disconnect = on_disconnect
#client.on_message = on_message

#
# MQTT Setup
#

from umqtt.simple import MQTTClient
MQTT_BROKER = 'broker.emqx.io'
MQTT_PORT = 1883


clinet = None
is_controller = None
is_player = None

def agent_init(conroller_or_player):
    global is_controller
    global is_player
    global client

    if conroller_or_player == 'controller':
        is_controller = True
        is_player = False
    else:
        is_controller = False
        is_player = True

    if is_controller:
        mqtt_client_id = 'cont_1234'    # adhoc!!
    else:
        mqtt_client_id = 'play_1234'    # adhoc!!
    
    client = MQTTClient(mqtt_client_id, MQTT_BROKER, MQTT_PORT)
    client.set_callback(on_message)
    
    client.connect()

    if is_controller:
        print('subscribe', f"{TOPIC_ROOT}/player/#")
        client.subscribe(f"{TOPIC_ROOT}/player/#")
    else:
        print('subscribe', TOPIC_COMMAND_CHANGE_STATE)  
        print('subscribe', TOPIC_GAME_SUMMARY)

        client.subscribe(TOPIC_COMMAND_CHANGE_STATE)  
        client.subscribe(TOPIC_GAME_SUMMARY)
    
    #client.check_msg()
    
    
    
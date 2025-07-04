#
# class GameAgent
# manage State Machine and communicate controller and players
# pc sample version
# file: ~/lang/py/mqtt/game_rk_game_agent/game_agent.py
#
# v0.07  2025/6/29 17:00
#    create game_agent
# v0.08  2025/6/29 22:00
#    6/29 final
# v0.09  2025/7/1 22:20
#    7/1 final
# v0.10  2025/7/2  22:05
#    Restructured function scopes for improved clarity and logic isolation
# v0.11  2025/7/3 
#    Restructured function scopes for improved clarity and logic isolation
# v0.12  2025/7/4
#    Restructured function scopes for improved clarity and logic isolation



from topic_defs import *
import datetime
import json
import pdb
import time


#
# MQTT Defs
#
import paho.mqtt.client as mqtt 
MQTT_BROKER = 'broker.emqx.io'
MQTT_PORT = 1883


GAME_DURATIN = 10   # time for click battle

INIT_STATE = 'STATE_OPEN'
current_state = None

# mqtt client

game_id = None

is_controller = False
is_player = False

game_member_status = {}
result = {}


#
# call back for update click info
# periodic process
#
CB_PLAYER_CREATE_REPORT = None
CB_PLAYER_DISP_STATUS = None


#
#
#
STATE_BEHAVIORS = {

    'STATE_OPEN' : {
       'topic' : TOPIC_COMMAND_CHANGE_STATE,
       'payload' : {'state' : 'STATE_OPEN'},
       'player_action' : None,
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
                     'game_member_status' : None,   # set in controller_action
# value in  _change_state_for_controller(next_state):

                     'winner' : None,  # set in controller_action
                   },
       'player_action' : None,
       'controller_action' : None,
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


def set_cb_func_for_controller(cb_name, func):
    if cb_name in STATE_BEHAVIORS:
        STATE_BEHAVIORS[cb_name]['controller_action'] = func
    else:
        print('Error in set_cb_func')
        print('unknown state name', cb_name)

def set_cb_func_for_player(cb_name, func):

    global CB_PLAYER_CREATE_REPORT
    global CB_PLAYER_DISP_STATUS

    if cb_name in STATE_BEHAVIORS:
        STATE_BEHAVIORS[cb_name]['player_action'] = func
    elif  cb_name == 'CB_PLAYER_CREATE_REPORT':
        CB_PLAYER_CREATE_REPORT = func
    elif  cb_name == 'CB_PLAYER_DISP_STATUS':
        CB_PLAYER_DISP_STATUS = func
    else:
        print('Error in set_cb_func')
        print('unknown cb_name', cb_name)

def get_current_state():
    return current_state

def get_next_state(state = None):
    if state is None:
       state = current_state
    return STATE_BEHAVIORS[state]['next_state']

def get_duration_to_transition(state):
    return STATE_BEHAVIORS[state]['duration']

def get_result():
    return result, game_member_status

#
#
#
#

def init(player_or_controller):
    global game_member_status
    global is_controller
    global is_player
    print('init')
    game_member_status = {}
    if player_or_controller == 'controller':
       is_controller = True
    if player_or_controller == 'player':
       is_player = True
    _connect()


def open_game_by_controller(gid):
    global game_id
    game_id = gid
    return change_state_by_controller('STATE_OPEN')


def _cbm_store_result(topic, payload):
    global result
    global game_member_status

    print('cbm_store_result------------------------------------------')
    if is_controller is False:
        payload_str = payload.decode('utf-8')
        payload_dic = json.loads(payload_str)
        result = payload_dic['winner']
        game_member_status = payload_dic['game_member_status']
        #import pdb
        #pdb.set_trace()

def _cbm_store_game_id(topic, payload):
    global game_id

    print('cbm_store_game_id------------------------------------------')
    if is_controller is False:
        payload_str = payload.decode('utf-8')
        payload_dic = json.loads(payload_str)
        game_id = payload_dic['game_id']

#
# return current_state
#
def _cbm_change_state_by_message(topic, payload):
    global current_state
    print('cs_b_msg')
    if topic != TOPIC_COMMAND_CHANGE_STATE:
       print('Error in change state by message')
       print('not collect topic', topic)
    payload_str = payload.decode('utf-8')
    payload_dic = json.loads(payload_str)
    state = payload_dic['state']
    if state == 'STATE_OPEN': 
         if is_controller is False:   
             _cbm_store_game_id(topic, payload)
    elif state == 'STATE_RESULT': 
         if is_controller is False:
             _cbm_store_result(topic, payload)
    if state in STATE_BEHAVIORS:
         val = _exec_player_action(state) 
         current_state = state
    else:
        print('Error ! no match next_state in STATE_BEHAVIORS', state)

    return current_state


#
# change state function
#
# return value:
#    current_state:  current state name
#    duration:  (wait time until transfer to next state)
#
cmd_seq = 0
def change_state_by_controller(state):
    global cmd_seq
    global current_state

    agent_ret_val = None
    cont_ret_val = None

    if not state in STATE_BEHAVIORS:
        print('Error ! no match next_state in STATE_BEHAVIORS', state)
        return (current_state, 0)
    else:
        cont_ret_val = _exec_controller_action(state, game_member_status)
        if is_player:
            ret_val = _exec_player_action(state)

        print(f'--- state transfer ->({state}) --')
        topic = STATE_BEHAVIORS[state]['topic']
        payload = STATE_BEHAVIORS[state]['payload']
        duration = STATE_BEHAVIORS[state]['duration']
        cmd_seq += 1
        payload['game_id'] = game_id
        payload['cmd_seq'] = cmd_seq
        payload['time_stamp'] = str(datetime.datetime.now())
        if state == 'STATE_RESULT':
            payload = payload | cont_ret_val
        print('publish:' , topic, payload)
        client.publish(topic, json.dumps(payload))
        current_state = state
        return  (current_state , duration)



def _exec_controller_action(state, game_member_status):
    val = None
    if 'controller_action' in STATE_BEHAVIORS[state]:
       func = STATE_BEHAVIORS[state]['controller_action']
       print('exec controller action:', func)
       #import pdb
       #pdb.set_trace()
       if func is not None:
            val = func(game_member_status)
    return val

def _exec_player_action(state):
    val = None
    if 'player_action' in STATE_BEHAVIORS[state]:
        func = STATE_BEHAVIORS[state]['player_action']
        if func is None:
             print('not defined function, skip', state)
             val = None
        else:
             val = func()
    return val




#
#   periodocally publish message
#
#
#    { <player_id> : { 'click_count' : 123  }, ... ,}
#  
#


def exec_game_agent_task():
     if is_controller:
          _send_to_player_game_member_status()
     else:
          _send_to_controller_player_status()


#   publish click summary  from controller to player via game_agent 
#   controller -----> game_agent  --->  player
#
#  publish every 0.5sec

last_send_status_time = 0
def _send_to_player_game_member_status():

    global last_send_status_time

    if current_state in ('STATE_OPEN', 'STATE_READY', 'STATE_RESULT', 'STATE_CLOSE'):
        pass
    else:
        if (time.time() - last_send_status_time) < 0.5:
            pass
        else: 
            print('send game member status to players')
            topic = TOPIC_GAME_SUMMARY
            payload = {
                   'game_id' : game_id,
                   'time_stamp' : str(datetime.datetime.now()), 
                   'game_member_status' : game_member_status,
            }
            client.publish(topic, json.dumps(payload))
            last_send_status_time = time.time()

#
#  send message fom  player to controller periodically
#  players status (click count)
#  player -----> game_agent  --->  controller
#

last_send_player_status_time = 0
def _send_to_controller_player_status():
    global last_send_player_status_time

    current_state = get_current_state()
    #print('current_state:', current_state)
    if current_state in ('STATE_OPEN', 'STATE_READY', 'STATE_RESULT', 'STATE_CLOSE'):
        pass
    else:
        if (time.time() - last_send_player_status_time) < 0.5:
            pass
        else: 
            print('send players status to controller')
            func = CB_PLAYER_CREATE_REPORT
            if func is None:
                print('at status report ,  cb func is None , so skip')
                return None
            else:
                topic = TOPIC_PLAYER_REPORT
                payload = func()
                payload['game_id'] = game_id
                #import pdb
                #pdb.set_trace()
                print('send(p->c): ' , topic, payload)
                client.publish(topic, json.dumps(payload))
                last_send_player_status_time = time.time()


#
#  receive message from player
#
#  player -> controller via game_agent  (status report)
#
#

def _cbm_receive_from_player_player_status(topic, payload):
    global game_member_status
    #import pdb
    #pdb.set_trace()
    payload_str = payload.decode('utf-8')
    payload_dic = json.loads(payload_str)
    player_id = payload_dic['player_id']
    if player_id in game_member_status:
        game_member_status[player_id]['click_count'] = payload_dic['click_count']
    else:
        game_member_status[player_id] = {
           'player_id' : payload_dic['player_id'],
           'player_nick_name' : payload_dic['player_nick_name'],
           'click_count' : payload_dic['click_count'],
        }


#
# 
# received  message (game summary ) from  controller via game_agent
#   game_agent w/controller --->  game_agent w/player
#
def _cbm_receive_from_controller_game_member_status(topic, payload):
    global game_member_status
    payload_str = payload.decode('utf-8')
    payload_dic = json.loads(payload_str)
    game_member_status = payload_dic['game_member_status']
    func = CB_PLAYER_DISP_STATUS
    if func is None:
        print('error! cb func is None==============================')
    else:
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        func(game_member_status)



#
# MQTT Setup
#


#
# MQTT Handlers
#

def on_connect(client, userdata, flag, rc):
    print("Connected with result code " + str(rc))
    if is_controller:
        print('subscribe', f"{TOPIC_ROOT}/player/#")
        client.subscribe(f"{TOPIC_ROOT}/player/#")
    elif is_player:
        client.subscribe(TOPIC_COMMAND_CHANGE_STATE)  
        client.subscribe(TOPIC_GAME_SUMMARY)
    else:
        print('Error i am not controller nor player!!')

def on_disconnect(client, userdata, rc):
  if  rc != 0:
    print("Unexpected disconnection.")


def on_message(client, userdata, msg):
    global current_state
    topic = msg.topic
    payload = msg.payload
    print('------------------')
    print("Received: ", topic , '   ' , payload)

    if is_controller:
        if topic == TOPIC_PLAYER_REPORT:
            # update player state
            _cbm_receive_from_player_player_status(topic, payload)
        else:
            print('Error!! unknown topic', topic)
    else:
        if 'player' in topic:
            pass  # skip if plyer in topic (send by me)
        elif topic == TOPIC_COMMAND_CHANGE_STATE:
            current_state = _cbm_change_state_by_message(topic, payload)
        elif topic == TOPIC_GAME_SUMMARY:
            _cbm_receive_from_controller_game_member_status(topic, payload)
        else:
            print('Error unkown topic', topic)
        

#
# setup MQTT
#

client = None
def _connect():
    global client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()


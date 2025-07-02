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
#

# 
# ==ZAN==  not implemeted  ==ZAN==
# if receive message from controller
# which shows game member summary
#

from topic_defs import *
import datetime
import json
import pdb

GAME_DURATIN = 10   # time for click battle

INIT_STATE = 'STATE_OPEN'
current_state = None

# mqtt client

game_id = None

is_controller = False
is_player = False

game_member_status = {}

def proc_agent_open_game():
    global game_id
    global game_member_status
    print('open_new_game')
    game_id = 'game_12345'
    game_member_status = {}


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
                     'game_member_status' : None,   # set in controller_action
# value in  _switch_to_state_for_controller(next_state):

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

#
# call back for update click info
# periodic process
#
CB_PUBLISH_REPORT_STATUS = None
CBM_RECEIVE_DISP_STATUS = None

def set_cb_func(cb_name, func, is_controller = False):

    global CB_PUBLISH_REPORT_STATUS
    global CBM_RECEIVE_DISP_STATUS


    if cb_name in STATE_BEHAVIORS:
        if is_controller:
            STATE_BEHAVIORS[cb_name]['controller_action'] = func
        else:
            STATE_BEHAVIORS[cb_name]['player_action'] = func
 
    elif  cb_name == 'CB_REPORT_STATUS':
        CB_PUBLISH_REPORT_STATUS = func
 
    elif  cb_name == 'CBM_DISP_STATUS':
        CBM_RECEIVE_DISP_STATUS = func

    else:
        print('Error in set_cb_func')
        print('unknown state name', cb_name)
        import pdb
        pdb.set_trace()

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

def switch_to_state(state):

    if is_controller:
        return _switch_to_state_for_controller(state)
    else:
        return _switch_to_state_for_player(state, None)

#
# return current_state
#
def switch_state_by_message(topic, payload):
    if topic != TOPIC_COMMAND_CHANGE_STATE:
       print('Error in switch state by message')
       print('not collect topic', topic)
    payload_str = payload.decode('utf-8')
    payload_dic = json.loads(payload_str)
    state = payload_dic['state']
    if state in STATE_BEHAVIORS:
         _switch_to_state_for_player(state, payload)
    else: 
       print('Error in switch state')
       print('can not find match topic', topic)
    return current_state

#
# state switch function for controller
#
# return value:
#    current_state:  current state name
#    duration:  (wait time until transfer to next state)
#
cmd_seq = 0
def _switch_to_state_for_controller(state):
    global cmd_seq
    global current_state

    agent_ret_val = None
    cont_ret_val = None

    if not state in STATE_BEHAVIORS:
        print('Error ! no match next_state in STATE_BEHAVIORS', state)
        return (current_state, 0)
    else:
        if state == 'STATE_READY':
            print('============== READY!!! ===============')

        agent_ret_val = _exec_agent_action(state)
        cont_ret_val = _exec_controller_action(state, game_member_status)
        if is_player:
            ret_val = _exec_player_action(state)

        print(f'--- state transfer ->({state}) --')
        print('next state:', state)
        topic = STATE_BEHAVIORS[state]['topic']
        payload = STATE_BEHAVIORS[state]['payload']
        duration = STATE_BEHAVIORS[state]['duration']
        payload['cmd_seq'] = cmd_seq
        payload['time_stamp'] = str(datetime.datetime.now())
        if state == 'STATE_RESULT':
            payload = payload | cont_ret_val
        print('publish:' , topic, payload)
        client.publish(topic, json.dumps(payload))
        cmd_seq += 1
        current_state = state
        return  (current_state , duration)

#
#
# state switch function for player
# return: current_state
#
def _switch_to_state_for_player(state, payload):
    global current_state

    if not state in STATE_BEHAVIORS:
        print('Error ! no match next_state in STATE_BEHAVIORS', state)
    else:
        val = _exec_agent_action(state)
        val = _exec_player_action(state, payload) 
        current_state = state

    return current_state

def _exec_agent_action(state):
    val = None
    if 'agent_action' in STATE_BEHAVIORS[state]:
       func = STATE_BEHAVIORS[state]['agent_action']
       if func is not None:
            val = func()
    return val

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

def _exec_player_action(state, payload):
    val = None
    if 'player_action' in STATE_BEHAVIORS[state]:
        func = STATE_BEHAVIORS[state]['player_action']
        if func is None:
             print('not defined function, skip', state)
             val = None
        else:
             if state == 'STATE_RESULT':
                  val = func(payload)
             else:
                  val = func()
    return val




#
#    { <player_id> : { 'click_count' : 123  }, ... ,}
#  
#


#
#   periodocally publish message

def exec_game_agent_task():
     if is_player:
          publish_click_report()
     else:
          publish_game_member_status()



#
#  send message fom  player to controller periodically
#  players status (click count)
#  player -----> game_agent  --->  controller
#

import time
last_click_report = 0
def publish_click_report():
    global last_click_report

    current_state = get_current_state()
    #print('current_state:', current_state)
    if current_state in ('STATE_OPEN', 'STATE_READY', 'STATE_RESULT', 'STATE_CLOSE'):
        #print('z ',end='')
        pass
    else:
        if (time.time() - last_click_report) < 0.5:
            #print('z ',end='')
            pass
        else: 
            print('report status to controller')
            func = CB_PUBLISH_REPORT_STATUS
            if func is None:
                print('at status report ,  cb func is None , so skip')
                import pdb
                pdb.set_trace()
                return None
            else:
                topic = TOPIC_PLAYER_REPORT
                payload = func()
                print('publish:' , topic, payload)
                client.publish(topic, payload)
                last_click_report = time.time()



#   publish click summary  from controller to player via game_agent 
#   controller -----> game_agent  --->  player
#
#  publish every 0.5sec

last_publish_status = 0
def publish_game_member_status():

    global last_publish_status

    if current_state in (
                'STATE_OPEN', 
                'STATE_READY', 
                'STATE_RESULT', 
                'STATE_CLOSE',
         ):
        pass
    else:

        if (time.time() - last_publish_status) < 0.5:
            #print('z ',end='')
            pass
        else: 
            print(f'publish summary in {current_state}')
            topic = TOPIC_GAME_SUMMARY
            payload = {
                   'game_id' : game_id,
                   'time_stamp' : str(datetime.datetime.now()), 
                   'game_member_status' : game_member_status,
            }
            client.publish(topic, json.dumps(payload))




#
#  receive message from player
#
#  player -> controller via game_agent  (status report)
#
#
def cbm_receive_message_from_player(topic, payload):
    global game_member_status
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
def cbm_receive_from_controller_member_status(topic, payload):
    global game_member_status
    payload_str = payload.decode('utf-8')
    payload_dic = json.loads(payload_str)
    game_member_status = payload_dic['game_member_status']
    func = CBM_RECEIVE_DISP_STATUS 
    if func is None:
        print('error! cb func is None==============================')
    else:
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        func(topic, payload)




#
# MQTT Setup
#

import paho.mqtt.client as mqtt 
MQTT_BROKER = 'broker.emqx.io'
MQTT_PORT = 1883


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

def on_disconnect(client, userdata, rc):
  if  rc != 0:
    print("Unexpected disconnection.")



# not in use
#def on_message(client, userdata, msg):
#    topic = msg.topic
#    payload = msg.payload
#    print("Received: ", topic , '   ' , payload)
#    #end_time = time.perf_counter()
#    #elapsed_time = end_time - start_time
#    #print(f"Elapsed time: {elapsed_time} seconds")


def on_message(client, userdata, msg):
    global current_state
    topic = msg.topic
    payload = msg.payload
    print('------------------')
    print("Received: ", topic , '   ' , payload)

    if is_controller:
        if topic == TOPIC_PLAYER_REPORT:
            # update player state
            cbm_receive_message_from_player(topic, payload)
        else:
            print('Error!! unknown topic', topic)
    else:
        if 'player' in topic:
            pass  # skip if plyer in topic (send by me)
        elif topic == TOPIC_COMMAND_CHANGE_STATE:
            current_state = switch_state_by_message(topic, payload)
        elif topic == TOPIC_GAME_SUMMARY:
            cbm_receive_from_controller_member_status(topic, payload)
        else:
            print('Error unkown topic', topic)
        

#
# setup MQTT
#

client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()


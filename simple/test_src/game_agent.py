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
# v0.13  2025/7/5
#    Refactored into class form
#    Moved the state transition table into the GameAgent class for encapsulation


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

GAME_DURATIN = 10   # Constant defining the duration of a click match
INIT_STATE = 'STATE_OPEN'



class GameAgent:

    def __init__(self, player_or_controller):

        self.current_state = None
        self.session_id = None
        self.is_controller = False
        self.is_player = False
        self.game_member_status = None
        self.result = None
 
        self.game_member_status = {}
        self.result = {}
        self.current_state = INIT_STATE
        self.client = None

        # var for periodic send message cycle
        self.last_send_player_status_time = 0
        self.last_send_status_time = 0


        #
        # call back for update click info
        # periodic process
        #
        self.CB_PLAYER_CREATE_REPORT = None
        self.CB_PLAYER_DISP_STATUS = None

        #
        #
        #
        self.STATE_BEHAVIORS = {

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

                     'result' : None,  # set in xxxxxx
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
        



        print('__init__')

        if player_or_controller == 'controller':
            self.is_controller = True
        elif player_or_controller == 'player':
            self.is_player = True
        elif player_or_controller == 'player_and_controller'  or player_or_controller == 'controller_and_player':  
            self.is_player = True
            self.is_controller = True
        else:
            print('Error in game_agent::init(), unkowon type', player_or_controller)
            return None
        self._MQTT_connect()





    def set_cb_func_for_controller(self, cb_name, func):

       if cb_name in self.STATE_BEHAVIORS:
           self.STATE_BEHAVIORS[cb_name]['controller_action'] = func
       else:
           print('Error in set_cb_func')
           print('unknown state name', cb_name)


    def set_cb_func_for_player(self, cb_name, func):

       if cb_name in self.STATE_BEHAVIORS:
           self.STATE_BEHAVIORS[cb_name]['player_action'] = func
       elif  cb_name == 'CB_PLAYER_CREATE_REPORT':
           self.CB_PLAYER_CREATE_REPORT = func
       elif  cb_name == 'CB_PLAYER_DISP_STATUS':
           self.CB_PLAYER_DISP_STATUS = func
       else:
           print('Error in set_cb_func')
           print('unknown cb_name', cb_name)
    
    
    def get_current_state(self):
        return self.current_state
    
    def get_next_state(self, state = None):
        if state is None:
           state = self.current_state
        return self.STATE_BEHAVIORS[state]['next_state']
    
    def get_duration_to_transition(self, state):
        return STATE_BEHAVIORS[state]['duration']
    
    def get_game_member_status(self):
        return self.game_member_status

    def get_result(self):
        return self.result
    
    #
    #
    #
    #
    
    def proc_game_agent_open(self):
        print('open')
        self.game_member_status = {}
        self.result = {}
    
    def open_game_by_controller(self, session_id):
        self.session_id = session_id
        return self.change_state_by_controller('STATE_OPEN')
    
    def _cbm_store_result(self, topic, payload):
    
        print('cbm_store_result------------------------------------------')
        if self.is_controller is False:
            payload_str = payload.decode('utf-8')
            payload_dic = json.loads(payload_str)
            self.result = payload_dic['result']
            self.game_member_status = payload_dic['game_member_status']
    
    def _cbm_store_session_id(self, topic, payload):

        print('cbm_store_session_id------------------------------------------')
        if self.is_controller is False:
            payload_str = payload.decode('utf-8')
            payload_dic = json.loads(payload_str)
            self.session_id = payload_dic['session_id']
    
    #
    # return current_state
    #
    def _cbm_change_state_by_message(self, topic, payload):

        print('cs_b_msg')
        if topic != TOPIC_COMMAND_CHANGE_STATE:
           print('Error in change state by message')
           print('not collect topic', topic)
        payload_str = payload.decode('utf-8')
        payload_dic = json.loads(payload_str)
        state = payload_dic['state']
        if state == 'STATE_OPEN': 
             if self.is_controller is False:   
                 self._cbm_store_session_id(topic, payload)
        elif state == 'STATE_RESULT': 
             if self.is_controller is False:
                 self._cbm_store_result(topic, payload)
        if state in self.STATE_BEHAVIORS:
             self._exec_player_action(state) 
             self.current_state = state
        else:
            print('Error ! no match next_state in STATE_BEHAVIORS', state)
    
        return self.current_state
    
    
    #
    # change state function
    #
    # return value:
    #    current_state:  current state name
    #    duration:  (wait time until transfer to next state)
    #
    cmd_seq = 0
    def change_state_by_controller(self, state):
    
        agent_ret_val = None
        cont_ret_val = None
    
        if not state in self.STATE_BEHAVIORS:
            print('Error ! no match next_state in STATE_BEHAVIORS', state)
            return (self.current_state, 0)
        else:
            if state == 'STATE_OPEN':
                 self.proc_game_agent_open()
            cont_ret_val = self._exec_controller_action(state)
            if self.is_player:
                 self._exec_player_action(state)
    
            print(f'--- state transfer ->({state}) --')
            topic = self.STATE_BEHAVIORS[state]['topic']
            payload = self.STATE_BEHAVIORS[state]['payload']
            duration = self.STATE_BEHAVIORS[state]['duration']
            self.cmd_seq += 1
            payload['session_id'] = self.session_id
            payload['cmd_seq'] = self.cmd_seq
            payload['time_stamp'] = str(datetime.datetime.now())
            payload['game_member_status'] = self.game_member_status
            if state == 'STATE_RESULT':
                payload['result'] = cont_ret_val
            print('publish:' , topic, payload)
            self.client.publish(topic, json.dumps(payload))
            self.current_state = state
            return  self.current_state , duration
    
    def _exec_controller_action(self, state):
        val = None
        if 'controller_action' in self.STATE_BEHAVIORS[state]:
           func = self.STATE_BEHAVIORS[state]['controller_action']
           if func is not None:
                val = func(self)
        return val

    def _exec_player_action(self, state):
        val = None
        if 'player_action' in self.STATE_BEHAVIORS[state]:
            func = self.STATE_BEHAVIORS[state]['player_action']
            if func is None:
                 print('not defined function, skip', state)
                 val = None
            else:
                 val = func(self)
        return val
    
    
    #
    #   periodocally publish message
    #
    #
    #    { <player_id> : { 'click_count' : 123  }, ... ,}
    #  
    #
    
    
    def exec_game_agent_task(self):
         if self.is_controller:
              self._send_to_player_game_member_status()
         else:
              self._send_to_controller_player_status()
    
    
    #   publish click summary  from controller to player via game_agent 
    #   controller -----> game_agent  --->  player
    #
    #  publish every 0.5sec
    
    def _send_to_player_game_member_status(self):
    
        if self.current_state in ('STATE_OPEN', 'STATE_READY', 'STATE_RESULT', 'STATE_CLOSE'):
            pass
        else:
            if (time.time() - self.last_send_status_time) < 0.5:
                pass
            else: 
                topic = TOPIC_GAME_SUMMARY
                payload = {
                       'session_id' : self.session_id,
                       'time_stamp' : str(datetime.datetime.now()), 
                       'game_member_status' : self.game_member_status,
                }
                print('send to players, game member status')
                print(topic, payload)
                self.client.publish(topic, json.dumps(payload))
                self.last_send_status_time = time.time()
    
    #
    #  send message fom  player to controller periodically
    #  players status (click count)
    #  player -----> game_agent  --->  controller
    #

    def _send_to_controller_player_status(self):

        if self.current_state in ('STATE_OPEN', 'STATE_READY', 'STATE_RESULT', 'STATE_CLOSE'):
            pass
        else:
            if (time.time() - self.last_send_player_status_time) < 0.5:
                pass
            else: 
                print('send players status to controller')
                func = self.CB_PLAYER_CREATE_REPORT
                if func is None:
                    print('at status report ,  cb func is None , so skip')
                    return None
                else:
                    topic = TOPIC_PLAYER_REPORT
                    status = func()
                    payload = status
                    payload['session_id'] = self.session_id
                    print('send(p->c): ' , topic, payload)
                    self.client.publish(topic, json.dumps(payload))
                    self.last_send_player_status_time = time.time()
    
    #
    #  receive message from player
    #
    #  player -> controller via game_agent  (status report)
    #
    #
    
    def _cbm_receive_from_player_player_status(self, topic, payload):
        payload_str = payload.decode('utf-8')
        payload_dic = json.loads(payload_str)
        player_id = payload_dic['player_id']
        if player_id in self.game_member_status:
            self.game_member_status[player_id]['click_count'] = payload_dic['click_count']
            self.game_member_status[player_id]['time_stamp'] = payload_dic['time_stamp']
        else:
            self.game_member_status[player_id] = payload_dic
    
    #
    # 
    # received  message (game summary ) from  controller via game_agent
    #   game_agent w/controller --->  game_agent w/player
    #
    def _cbm_receive_from_controller_game_member_status(self, topic, payload):

        payload_str = payload.decode('utf-8')
        payload_dic = json.loads(payload_str)
        self.game_member_status = payload_dic['game_member_status']
        func = self.CB_PLAYER_DISP_STATUS
        if func is None:
            print('error! cb func is None==============================')
        else:
            print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            func(self.game_member_status)



    #
    # setup MQTT
    #
    def _MQTT_connect(self):
        self.client = mqtt.Client()
        if self.is_controller:
            self.client.on_connect = self.on_connect_for_controller
        else:
            self.client.on_connect = self.on_connect_for_player
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.client.loop_start()

    #========================================
    #
    # MQTT callback functions
    #
    #========================================
    
    def on_connect_for_controller(self, client, userdata, flag, rc):
        print("Connected with result code " + str(rc))
        print('subscribe', f"{TOPIC_ROOT}/player/#")
        self.client.subscribe(f"{TOPIC_ROOT}/player/#")
    
    def on_connect_for_player(self, client, userdata, flag, rc):
        print("Connected with result code " + str(rc))
        self.client.subscribe(TOPIC_COMMAND_CHANGE_STATE)  
        self.client.subscribe(TOPIC_GAME_SUMMARY)
    
    def on_disconnect(self, client, userdata, rc):
      if  rc != 0:
        print("Unexpected disconnection.")
    
    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload
        print('------------------')
        print("Received: ", topic , '   ' , payload)
    
        if self.is_controller:
            if topic == TOPIC_PLAYER_REPORT:
                # update player state
                self._cbm_receive_from_player_player_status(topic, payload)
            else:
                print('Error!! unknown topic', topic)
        else:
            if 'player' in topic:
                pass  # skip if plyer in topic (send by me)
            elif topic == TOPIC_COMMAND_CHANGE_STATE:
                self.current_state = self._cbm_change_state_by_message(topic, payload)
            elif topic == TOPIC_GAME_SUMMARY:
                self._cbm_receive_from_controller_game_member_status(topic, payload)
            else:
                print('Error unkown topic', topic)
            
    
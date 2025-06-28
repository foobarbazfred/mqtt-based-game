#
# Finit State Machine
#

from topic_defs import *

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


GAME_DURATIN = 10   # time for click battle

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

def switch_to_state(next_state,function_table):
    global current_state
    invoke_function(STATE_BEHAVIORS[next_state]['function'],function_table)
    current_state = next_state

def invoke_function(func_name,function_table):
    if func_name in function_table:
       return function_table[func_name]()
    else:
       print('Error unknown function:', func_name)
       return None


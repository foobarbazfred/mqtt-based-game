#!/usr/bin/python3

#  
# controller sample code for MQTT Renda OH
# pc sample version
# file: ~/lang/py/mqtt/game_rk_game_agent/controller.py
#
# PC Sample Version
# v0.04  2025/6/28 refactor, 
#    Extracted FSM components into a separate module
# v0.05  2025/6/29 refactor, 
#    refine FSM and push method into FSM
# v0.07  2025/6/29 17:00
#    refine FSM and push method into FSM
# v0.08  2025/6/29 21:00
#    refine timing
# v0.09  2025/6/29 22:00
#    6/29 final
# v0.10  2025/7/1 21:00
#    7/1 final
# v0.11  2025/7/2  22:05
#    Restructured function scopes for improved clarity and logic isolation
#


import datetime
import time
import json

PLAYER_ID = 'pc_py_0002'
PLAYER_NICK_NAME = 'pcpy02'

#from fsm import STATE_BEHAVIORS
#from fsm import STATE_READY

from topic_defs import *
import game_agent
game_agent.is_controller = True


def proc_controller_find_winner(game_member_status):
    payload = {
        'game_member_status' : game_member_status,
        'winner' : 'id_0123_win',
        'time_stamp' : str(datetime.datetime.now()),
    }
    return payload

game_agent.set_cb_func('STATE_RESULT', proc_controller_find_winner, is_controller=True)


def game_sequence():

    current_state = None
    last_state_transfer = 0
    duration = 0
    cmd_seq = 0

    game_agent.init_state()
    current_state = game_agent.get_current_state()
    duration = game_agent.get_duration_to_transition(current_state)
    last_state_transfer = time.time()

    while True:
       
        # kick game_agent_task 
        game_agent.exec_game_agent_task()

        # check trans to next state
        if (time.time() - last_state_transfer ) <  duration:
            pass
            #print('not now state change')
            time.sleep(0.5)
        else:
            #  
            # switch to next state
            #  
            current_state, duration = game_agent.switch_to_next_state()
            print('wait for ...', duration)
            if current_state == 'STATE_CLOSE' :
                break
            #import pdb
            #pdb.set_trace()
            last_state_transfer = time.time()
            # for debug (accell)
            #last_state_transfer = 0
    
def controller_main_loop():
    while True:
        print('game start')
        game_sequence()
        print('game finished')
	

controller_main_loop()











#!/usr/bin/python3

#
# player sample code for MQTT Renda Oh
#
# PC Sample Version
# v0.04  2025/6/28 refactor, 
#    Extracted FSM components into a separate module
# v0.05  2025/6/29 refactor, 
#    refine FSM and push method into FSM
# v0.06  2025/6/29 refactor, 
#    refine FSM to game_agent
# v0.07  2025/6/29 17:00
#    refine
#

import time
import json
import paho.mqtt.client as mqtt 
import pdb

MQTT_BROKER = 'broker.emqx.io'
MQTT_PORT = 1883

PLAYER_ID = 'pc_py_0001'
PLAYER_NICK_NAME = 'pcpy01'

click_count = 0


from topic_defs import *
import game_agent
game_agent.is_player = True
game_agent.init_state()
current_state = game_agent.get_current_state()

#pdb.set_trace()


#
# player's procedure
#

def proc_player_open():
    global click_count
    print('cb func: open')
    click_count = 0

def proc_player_ready():
    print('cb func: ready')

def proc_player_countdown_to_start_3():
    print('cb func: cdts3')

def proc_player_countdown_to_start_2():
    print('cb func: cdts2')

def proc_player_countdown_to_start_1():
    print('cb func: cdts1')

def proc_player_start():
    print('cb func: start')

def proc_player_countdown_to_stop_3():
    print('cb func: cdtp3')

def proc_player_countdown_to_stop_2():
    print('cb func: cdtp2')

def proc_player_countdown_to_stop_1():
    print('cb func: cdtp1')

def proc_player_stop():
    print('cb func: stop')

def proc_player_result():
    print('cb func: result')

def proc_player_close():
    print('cb func: close')

game_agent.set_cb_func('STATE_OPEN', proc_player_open)
game_agent.set_cb_func('STATE_READY', proc_player_ready)
game_agent.set_cb_func('STATE_COUNTDOWN_TO_START_3', proc_player_countdown_to_start_3)
game_agent.set_cb_func('STATE_COUNTDOWN_TO_START_2', proc_player_countdown_to_start_2)
game_agent.set_cb_func('STATE_COUNTDOWN_TO_START_1',  proc_player_countdown_to_start_1)
game_agent.set_cb_func('STATE_START', proc_player_start)
game_agent.set_cb_func('STATE_COUNTDOWN_TO_STOP_3', proc_player_countdown_to_stop_3)
game_agent.set_cb_func('STATE_COUNTDOWN_TO_STOP_2', proc_player_countdown_to_stop_2)
game_agent.set_cb_func('STATE_COUNTDOWN_TO_STOP_1', proc_player_countdown_to_stop_1)
game_agent.set_cb_func('STATE_STOP', proc_player_stop)
game_agent.set_cb_func('STATE_RESULT', proc_player_result)
game_agent.set_cb_func('STATE_CLOSE', proc_player_close)




last_state_transfer = 0
duration = 0

#
# main function
#

def player_main_loop():
    global click_count
    while True:
        click_count += 1
        current_state = game_agent.get_current_state()
        print('current_state:', current_state)
        if current_state in ('STATE_OPEN', 'STATE_READY', 'STATE_RESULT', 'STATE_CLOSE'):
            print('z ',end='')
        else:
            print('report status to controller')
            game_agent.proc_agent_status_report(PLAYER_ID, PLAYER_NICK_NAME, click_count)
        time.sleep(0.5)

player_main_loop()

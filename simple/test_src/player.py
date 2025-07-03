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
# v0.08  2025/6/29 22:00
#    6/29 final
# v0.09  2025/7/1 22:20
#    7/1 
# v0.10  2025/7/1 22:30
#    7/1 final change calling function
# v0.11  2025/7/2 22:05
#    Restructured function scopes for improved clarity and logic isolation
# v0.12  2025/7/3
#    Restructured function scopes for improved clarity and logic isolation
#    
#

import datetime
import time
import json
import paho.mqtt.client as mqtt 
import pdb

MQTT_BROKER = 'broker.emqx.io'
MQTT_PORT = 1883

PLAYER_ID = 'pc_py_0001'
PLAYER_NICK_NAME = 'pcpy01'

click_count = 0
stop_flag = True


from topic_defs import *
import game_agent

#pdb.set_trace()


#
# player's procedure
#

def proc_player_open():
    global click_count
    global stop_flag

    print('cb func: open')
    click_count = 0
    stop_flag = True


def proc_player_ready():
    print('cb func: ready')

def proc_player_countdown_to_start_3():
    print('cb func: cdts3')

def proc_player_countdown_to_start_2():
    print('cb func: cdts2')

def proc_player_countdown_to_start_1():
    print('cb func: cdts1')

def proc_player_start():
    global click_count
    global stop_flag
    click_count = 0
    stop_flag = False
    print('cb func: start')

def proc_player_countdown_to_stop_3():
    print('cb func: cdtp3')

def proc_player_countdown_to_stop_2():
    print('cb func: cdtp2')

def proc_player_countdown_to_stop_1():
    print('cb func: cdtp1')

def proc_player_stop():
    global click_count
    global stop_flag

    stop_flag = True
    print('cb func: stop')

def proc_player_result():
    print('cb func: result')
    print('WWWWWWWWWWWWWWWWWIIIIIIIIIIIIIINNNNNNNNNNNNNNNNNNN')
    #print('result:', payload)
    result, game_member_status = game_agent.get_result()
    print('winner:', result)
    print('status:', game_member_status)
    print('--=====---------------------=============---------')



def proc_player_close():
    print('cb func: close')


#
#  not use game_member_status
#
def proc_player_report_status():
    global click_count
    global stop_flag

    print('cb func: get click')    
    print('RRRRR')
    if stop_flag is False:
        click_count += 1
    payload = json.dumps({
          'click_count': click_count,
          'player_id' : PLAYER_ID,
          'player_nick_name' : PLAYER_NICK_NAME,
          'time_stamp' : str(datetime.datetime.now()),
    })
    return  payload

def proc_player_display_status(topic, payload):
    print('cb func: display member status')    
    payload_str = payload.decode('utf-8')
    payload_dic = json.loads(payload_str)
    print('--=========--> [  ] <------=============---------')
    print(payload_dic['game_member_status'])
    print('--=====---------------------=============---------')


game_agent.set_cb_func_for_player('STATE_OPEN', proc_player_open)
game_agent.set_cb_func_for_player('STATE_READY', proc_player_ready)
game_agent.set_cb_func_for_player('STATE_COUNTDOWN_TO_START_3', proc_player_countdown_to_start_3)
game_agent.set_cb_func_for_player('STATE_COUNTDOWN_TO_START_2', proc_player_countdown_to_start_2)
game_agent.set_cb_func_for_player('STATE_COUNTDOWN_TO_START_1',  proc_player_countdown_to_start_1)
game_agent.set_cb_func_for_player('STATE_START', proc_player_start)
game_agent.set_cb_func_for_player('STATE_COUNTDOWN_TO_STOP_3', proc_player_countdown_to_stop_3)
game_agent.set_cb_func_for_player('STATE_COUNTDOWN_TO_STOP_2', proc_player_countdown_to_stop_2)
game_agent.set_cb_func_for_player('STATE_COUNTDOWN_TO_STOP_1', proc_player_countdown_to_stop_1)
game_agent.set_cb_func_for_player('STATE_STOP', proc_player_stop)
game_agent.set_cb_func_for_player('STATE_RESULT', proc_player_result)
game_agent.set_cb_func_for_player('STATE_CLOSE', proc_player_close)
game_agent.set_cb_func_for_player('CB_REPORT_STATUS', proc_player_report_status)
game_agent.set_cb_func_for_player('CBM_DISP_STATUS', proc_player_display_status)





last_state_transfer = 0
duration = 0

#
# main function
#


def player_main_loop():
    #game_agent.is_player = True
    game_agent.init('player')
    while True:
        game_agent.exec_game_agent_task()


player_main_loop()

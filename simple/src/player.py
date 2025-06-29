# player code for MQTT Renda Oh
#
# MicroPython version
#
# v0.04  2025/6/28 refactor, 
#    Extracted FSM components into a separate module
# v0.05  2025/6/29 refactor, 
#    refine FSM and push method into FSM
# v0.06  2025/6/29 refactor, 
#    refine FSM to game_agent
# v0.07  2025/6/29 17:00
#    refine
# v0.08  2025/6/29 21:00
#    Refine timing control
#

import time
import json

PLAYER_ID = 'pr_pico_0001'
PLAYER_NICK_NAME = 'pico01'

click_count = 0

from topic_defs import *
import game_agent
game_agent.agent_init('player')
game_agent.init_state()
current_state = game_agent.get_current_state()


#
# player's procedure
#

def proc_player_open():
    global click_count
    print('cb func: open')
    print('set count to 0')
    click_count = 0

def proc_player_ready():
    print('cb func: ready')

def proc_player_countdown_to_start_3():
    print('cb func: cdts3')
    play_sound('count_down')

def proc_player_countdown_to_start_2():
    print('cb func: cdts2')
    play_sound('count_down')

def proc_player_countdown_to_start_1():
    print('cb func: cdts1')
    play_sound('count_down')

def proc_player_start():
    print('cb func: start')
    play_sound('start')

def proc_player_countdown_to_stop_3():
    print('cb func: cdtp3')
    play_sound('count_down')

def proc_player_countdown_to_stop_2():
    print('cb func: cdtp2')
    play_sound('count_down')

def proc_player_countdown_to_stop_1():
    print('cb func: cdtp1')
    play_sound('count_down')

def proc_player_stop():
    print('cb func: stop')
    play_sound('stop')

def proc_player_result():
    print('cb func: result')
    play_sound('winner')

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
# buzzer
#
from machine import Pin
from machine import PWM
buzzer = PWM(Pin(17))

def play_sound(type):

    if type == 'count_down':
       buzzer.freq(700)
       buzzer.duty_u16(32768) 
       time.sleep(0.08)
       buzzer.duty_u16(0) 

    elif type == 'start':
       buzzer.freq(1100)
       buzzer.duty_u16(32768) 
       time.sleep(0.08)
       buzzer.duty_u16(0) 

    elif type == 'stop':
       buzzer.freq(1100)
       buzzer.duty_u16(32768) 
       time.sleep(0.08)
       buzzer.duty_u16(0) 

    elif type == 'winner':
       buzzer.freq(780)
       buzzer.duty_u16(32768) 
       time.sleep(0.1)
       buzzer.duty_u16(0) 
       time.sleep(0.1)
       buzzer.freq(1100)
       buzzer.duty_u16(32768) 
       time.sleep(0.2)
       buzzer.duty_u16(0) 

    elif type == 'loser':
       buzzer.freq(150)
       buzzer.duty_u16(32768) 
       time.sleep(0.1)
       buzzer.duty_u16(0) 
       time.sleep(0.1)
       buzzer.duty_u16(32768) 
       time.sleep(0.2)
       buzzer.duty_u16(0) 



#
# main function
#

def player_main_loop():
    global click_count
    last_report_time = 0
    while True:

        # dispatch check message in game_agent
        game_agent.client.check_msg()

        current_state = game_agent.get_current_state()
        #print('current_state:', current_state)
        if current_state in ('STATE_OPEN', 'STATE_RESULT', 'STATE_CLOSE',
        ):
            #print('.', end='')
            pass
        else:
            if time.ticks_diff(time.ticks_ms(), last_report_time) > 800:  # if over 500ms
                 print('report status to controller')
                 game_agent.proc_agent_status_report(PLAYER_ID, PLAYER_NICK_NAME, click_count)
                 last_report_time = time.ticks_ms()
    

player_main_loop()



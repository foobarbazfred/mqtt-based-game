#
# player class of MQTT Renda Oh
#
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
# v0.13  2025/7/5
#    Refactored into class form
# v0.14  2025/7/6
#    porting to MicroPython, game log fine tuning
# v0.15  2025/7/14
#    define costant for NeoPixel number of LED 
# v0.16  2025/8/2
#    Refactor GamePlayer initialization to accept UI config dictionary
#    
#

import time
import random
from mylib import timestamp
import ui
import pio_switch_counter

from machine import PWM
from machine import Pin
#
# neopixel
#
import neopixel

DEFAULT_GPIO_SWITCH = 0
DEFAULT_GPIO_SPEAKER = 16
DEFAULT_GPIO_NEOPIXEL = 17
DEFAULT_NEOPIXEL_LED_SIZE = 24

DEFAULT_UI_CONFIG = {
   'GPIO_SWITCH' : DEFAULT_GPIO_SWITCH,
   'GPIO_SPEAKER' : DEFAULT_GPIO_SPEAKER,
   'GPIO_NEOPIXEL' : DEFAULT_GPIO_NEOPIXEL,
   'NEOPIXEL_LED_SIZE' : DEFAULT_NEOPIXEL_LED_SIZE
}


class GamePlayer:

    def __init__(self, game_agent, id, nick_name, ui_config = None ):

        self.player_id = id
        self.player_nick_name = nick_name
        self.stop_flag = True
        self.click_count = 0
        self.game_agent = game_agent
        self.ui_config = DEFAULT_UI_CONFIG

        if ui_config is not None:
           if 'GPIO_SWITCH' in ui_config:
               self.ui_config['GPIO_SWITCH'] = ui_config['GPIO_SWITCH']
           if 'GPIO_SPEAKER' in ui_config:
               self.ui_config['GPIO_SPEAKER'] = ui_config['GPIO_SPEAKER']
           if 'GPIO_NEOPIXEL' in ui_config:
               self.ui_config['GPIO_NEOPIXEL'] = ui_config['GPIO_NEOPIXEL']
           if 'NEOPIXEL_LED_SIZE' in ui_config:
               self.ui_config['NEOPIXEL_LED_SIZE'] = ui_config['NEOPIXEL_LED_SIZE']

        self.game_agent.set_cb_func_for_player('STATE_OPEN', self.proc_player_open)
        self.game_agent.set_cb_func_for_player('STATE_READY', self.proc_player_ready)
        self.game_agent.set_cb_func_for_player('STATE_COUNTDOWN_TO_START_3', self.proc_player_countdown_to_start_3)
        self.game_agent.set_cb_func_for_player('STATE_COUNTDOWN_TO_START_2', self.proc_player_countdown_to_start_2)
        self.game_agent.set_cb_func_for_player('STATE_COUNTDOWN_TO_START_1', self. proc_player_countdown_to_start_1)
        self.game_agent.set_cb_func_for_player('STATE_START', self.proc_player_start)
        self.game_agent.set_cb_func_for_player('STATE_COUNTDOWN_TO_STOP_3', self.proc_player_countdown_to_stop_3)
        self.game_agent.set_cb_func_for_player('STATE_COUNTDOWN_TO_STOP_2', self.proc_player_countdown_to_stop_2)
        self.game_agent.set_cb_func_for_player('STATE_COUNTDOWN_TO_STOP_1', self.proc_player_countdown_to_stop_1)
        self.game_agent.set_cb_func_for_player('STATE_STOP', self.proc_player_stop)
        self.game_agent.set_cb_func_for_player('STATE_RESULT', self.proc_player_result)
        self.game_agent.set_cb_func_for_player('STATE_CLOSE', self.proc_player_close)
        self.game_agent.set_cb_func_for_player('CB_PLAYER_DISP_STATUS', self.proc_player_display_game_member_status)
        self.game_agent.set_cb_func_for_player('CB_PLAYER_CREATE_REPORT', self.proc_player_report_status)    

        self.np = neopixel.NeoPixel(Pin(self.ui_config['GPIO_NEOPIXEL']), self.ui_config['NEOPIXEL_LED_SIZE'])
        self.buzzer = PWM(Pin(self.ui_config['GPIO_SPEAKER']))    
        self.pio_sm = pio_switch_counter.init(Pin(self.ui_config['GPIO_SWITCH'], Pin.IN, Pin.PULL_UP))

    #
    # main loop
    #
    def main_loop(self):
        while True:
            self.game_agent.exec_game_agent_task()


    #
    #  players status (click count)
    #
    def proc_player_report_status(self):
    
        print('cb func: report status')    
        if self.stop_flag is False:
            self.click_count = pio_switch_counter.get_counter(self.pio_sm)
        status = {
              'click_count': self.click_count,
              'player_id' : self.player_id,
              'player_nick_name' : self.player_nick_name,
              'time_stamp' : timestamp()
        }
        return status
    
    
    #
    # player's procedure
    #
    
    def proc_player_open(self, game_agent):
        print('cb func: open')
        self.click_count = 0
        self.stop_flag = True
        ui.np_clear(self.np)
        self.pio_sm.restart()
    
    def proc_player_ready(self, game_agent):
        print('cb func: ready')
        ui.np_light_neo(self.np, '3p')
    
    def proc_player_countdown_to_start_3(self, game_agent):
        print('cb func: cdts3')
        ui.np_light_neo(self.np, 'c3')
        ui.play_sound(self.buzzer, 'c3')    

    def proc_player_countdown_to_start_2(self, game_agent):
        print('cb func: cdts2')
        ui.np_light_neo(self.np, 'c2')
        ui.play_sound(self.buzzer, 'c2')
    
    def proc_player_countdown_to_start_1(self, game_agent):
        print('cb func: cdts1')
        ui.np_light_neo(self.np, 'c1')
        ui.play_sound(self.buzzer, 'c1')
    
    def proc_player_start(self, game_agent):
        print('cb func: start')
        self.click_count = 0
        self.stop_flag = False
        ui.np_light_neo(self.np, 'c0')
        ui.play_sound(self.buzzer, 'c0')
    
    def proc_player_countdown_to_stop_3(self, game_agent):
        print('cb func: cdtp3')
        ui.play_sound(self.buzzer, 'c3')    
    
    def proc_player_countdown_to_stop_2(self, game_agent):
        print('cb func: cdtp2')
        ui.play_sound(self.buzzer, 'c2')    
    
    def proc_player_countdown_to_stop_1(self, game_agent):
        print('cb func: cdtp1')
        ui.play_sound(self.buzzer, 'c1')    
    
    def proc_player_stop(self, game_agent):
        print('cb func: stop')
        self.stop_flag = True
        ui.play_sound(self.buzzer, 'c0')    
    
    def proc_player_result(self, game_agent):
        print('cb func: game result')
        print('---result--------------------')
        result = game_agent.get_result()
        winner = result['winner']
        game_member_status = game_agent.get_game_member_status()
        print('winner:', winner)
        print('status:', game_member_status)
        if winner == self.player_id:
            print('WWWWWWWWWWWWWWWWWIIIIIIIIIIIIIINNNNNNNNNNNNNNNNNNN')
            ui.play_sound(self.buzzer, 'winner')
        else:
            print('xxxxxxxxxxxxxxxxxxxxxxxxxx')
            ui.play_sound(self.buzzer, 'loser')
        print('--=====---------------------=============---------')
    
    
    #print(f'---------------------------------{type(result)}')
    
    def proc_player_close(self, game_agent):
        print('cb func: close')
    
    def proc_player_display_game_member_status(self, game_member_status):
        opponent_max_clicks = 0
        my_click_count = 0
        opponent_member_clicks = []
        print('cb func: display game member status')    
        print('--=========--> [  ] <------=============---------')
        print(game_member_status)
        print('--=====---------------------=============---------')

        for id in game_member_status.keys():
            if id == self.player_id:
                my_click_count = game_member_status[id]['click_count']
            else:
                opponent_member_clicks.append(game_member_status[id]['click_count'])
        if len(opponent_member_clicks) > 0:
            opponent_max_clicks = max(opponent_member_clicks)
        else:
            opponent_max_clicks = 0
        print('ui.np_light_progress:' , my_click_count, opponent_max_clicks)
        ui.np_light_progress(self.np, my_click_count, opponent_max_clicks)


#
# end of file
#

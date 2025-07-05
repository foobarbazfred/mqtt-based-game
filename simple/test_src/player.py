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
# v0.13  2025/7/5
#    Refactored into class form
#    
#

import datetime
import time
import json
import paho.mqtt.client as mqtt 
import pdb
import random


from game_agent import GameAgent
from game_agent import set_cb_func_for_player


class GamePlayer:

    def __init__(self, id, nick_name):
        self.game_agent = GameAgent('player')
        self.player_id = id
        self.player_nick_name = nick_name
        self.stop_flag = True
        self.click_count = 0

        set_cb_func_for_player('STATE_OPEN', self.proc_player_open)
        set_cb_func_for_player('STATE_READY', self.proc_player_ready)
        set_cb_func_for_player('STATE_COUNTDOWN_TO_START_3', self.proc_player_countdown_to_start_3)
        set_cb_func_for_player('STATE_COUNTDOWN_TO_START_2', self.proc_player_countdown_to_start_2)
        set_cb_func_for_player('STATE_COUNTDOWN_TO_START_1', self. proc_player_countdown_to_start_1)
        set_cb_func_for_player('STATE_START', self.proc_player_start)
        set_cb_func_for_player('STATE_COUNTDOWN_TO_STOP_3', self.proc_player_countdown_to_stop_3)
        set_cb_func_for_player('STATE_COUNTDOWN_TO_STOP_2', self.proc_player_countdown_to_stop_2)
        set_cb_func_for_player('STATE_COUNTDOWN_TO_STOP_1', self.proc_player_countdown_to_stop_1)
        set_cb_func_for_player('STATE_STOP', self.proc_player_stop)
        set_cb_func_for_player('STATE_RESULT', self.proc_player_result)
        set_cb_func_for_player('STATE_CLOSE', self.proc_player_close)
        set_cb_func_for_player('CB_PLAYER_DISP_STATUS', self.proc_player_display_game_member_status)
        set_cb_func_for_player('CB_PLAYER_CREATE_REPORT', self.proc_player_report_status)    
    

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
            self.click_count += random.choice((0,1,1,1,2))
        status = {
              'click_count': self.click_count,
              'player_id' : self.player_id,
              'player_nick_name' : self.player_nick_name,
              'time_stamp' : str(datetime.datetime.now()),
        }
        return status
    

    
    #
    # player's procedure
    #
    
    def proc_player_open(self, game_agent):
        global click_count
        global stop_flag
    
        print('cb func: open')
        click_count = 0
        stop_flag = True
    
    
    def proc_player_ready(self, game_agent):
        print('cb func: ready')
    
    def proc_player_countdown_to_start_3(self, game_agent):
        print('cb func: cdts3')
    
    def proc_player_countdown_to_start_2(self, game_agent):
        print('cb func: cdts2')
    
    def proc_player_countdown_to_start_1(self, game_agent):
        print('cb func: cdts1')
    
    def proc_player_start(self, game_agent):
        self.click_count = 0
        self.stop_flag = False
        print('cb func: start')
    
    def proc_player_countdown_to_stop_3(self, game_agent):
        print('cb func: cdtp3')
    
    def proc_player_countdown_to_stop_2(self, game_agent):
        print('cb func: cdtp2')
    
    def proc_player_countdown_to_stop_1(self, game_agent):
        print('cb func: cdtp1')
    
    def proc_player_stop(self, game_agent):
        global click_count
        global stop_flag
    
        stop_flag = True
        print('cb func: stop')
    
    def proc_player_result(self, game_agent):
        print('cb func: game result')
        print('WWWWWWWWWWWWWWWWWIIIIIIIIIIIIIINNNNNNNNNNNNNNNNNNN')
        result = game_agent.get_result()
        game_member_status = game_agent.get_game_member_status()
        #import pdb
        #pdb.set_trace()
        print('winner:', result['winner'])
        print('status:', game_member_status)
        print('--=====---------------------=============---------')
    
    
    #print(f'---------------------------------{type(result)}')
    
    def proc_player_close(self, game_agent):
        print('cb func: close')
    
    def proc_player_display_game_member_status(self, game_member_status):
        print('cb func: display game member status')    
        print('--=========--> [  ] <------=============---------')
        print(game_member_status)
        print('--=====---------------------=============---------')
    
    

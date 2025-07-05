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
# v0.12  2025/7/3
#    Restructured function scopes for improved clarity and logic isolation
# v0.13  2025/7/4
#    Restructured function scopes for improved clarity and logic isolation
# v0.15  2025/7/5
#    Refactored into class form
#


import datetime
import time
import json
import random
from game_agent import GameAgent
from game_agent import set_cb_func_for_controller




class GameController:
 
    def __init__(self):
        self.session_id = None
        self.game_agent = GameAgent('controller')
        set_cb_func_for_controller('STATE_RESULT', self.proc_controller_make_result)

    def main_loop(self):
        while True:
            self.session_id = 'game_session_123_' + random.choice(('x','y','x'))
            print(f'game start ({self.session_id})')
            self.game_sequence()
            print(f'game finished ({self.session_id})')


    def game_sequence(self):
    
        current_state = None
        last_state_transfer = 0
        duration = 0
        cmd_seq = 0
    
        current_state, duration = self.game_agent.open_game_by_controller(self.session_id)
        last_state_transfer = time.time()
    
        while current_state != 'STATE_CLOSE':
           
            # kick game_agent_task 
            self.game_agent.exec_game_agent_task()
    
            # check trans to next state
            if (time.time() - last_state_transfer ) <  duration:
                pass
            else:
                #  
                # switch to next state
                #  
                next_state = self.game_agent.get_next_state()
                current_state, duration = self.game_agent.change_state_by_controller(next_state)
                print('wait for ...', duration)
                #import pdb
                #pdb.set_trace()
                last_state_transfer = time.time()
                # for debug (accell)
                #last_state_transfer = 0
        

    def proc_controller_make_result(self, game_agent):
        game_member_status = game_agent.get_game_member_status()
        max_click_count = 0
        top_click_user = None
        for id in game_member_status.keys():
             if game_member_status[id]['click_count'] > max_click_count: 
                 top_click_user = id
                 max_click_count = game_member_status[id]['click_count']
        result = {
            'winner' : top_click_user,
        }
        return result


        
    


    
    
    
    
    
    
    
    
    
    
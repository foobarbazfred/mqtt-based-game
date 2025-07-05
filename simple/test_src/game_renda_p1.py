#!/usr/bin/python3

from controller  import GameController
from player import GamePlayer
from game_agent import GameAgent


def main():

    is_player = True
    is_controller = False
    
    if is_controller:
    
        game_agent = GameAgent('controller')
        #
        # start Game Controller
        #
        game_controller = GameController(game_agent)
        game_controller.main_loop()
    

    if is_player:
    
       game_agent = GameAgent('player')

       player_id = 'id_0001'
       player_nick_name = 'i_am_p1'
    
       game_player = GamePlayer(game_agent, player_id, player_nick_name)
       game_player.main_loop()
    
    


    
main()
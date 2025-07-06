#
# MQTT Game Renda OH 
#  main function
#
#
from controller  import GameController
from player import GamePlayer
from game_agent import GameAgent
from mylib import get_uniq_id

def main():

    is_controller = True
    is_player = False
    
    if is_controller:
    
        game_agent = GameAgent('controller')
        #
        # start Game Controller
        #
        game_controller = GameController(game_agent)
        game_controller.main_loop()
    

    if is_player:
    
       game_agent = GameAgent('player')

       player_id = get_uniq_id('pico2w_', length=8)
       player_nick_name = 'go_1234'
    
       game_player = GamePlayer(game_agent, player_id, player_nick_name)
       game_player.main_loop()
    
    
main()



#
#
#
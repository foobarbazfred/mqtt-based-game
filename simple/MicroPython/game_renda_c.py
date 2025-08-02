#
# MQTT Game Renda OH for Game Controller
#
#  main function
#  v0.02  Code optimization: 
#  v0.03 (2025/8/2)
#

#
#
from controller  import GameController
from game_agent import GameAgent
from mylib import get_uniq_id

def main():
    
    game_agent = GameAgent('controller')

    #
    # start Game Controller
    #
    game_controller = GameController(game_agent)
    game_controller.main_loop()
    
    
main()



#
#
#
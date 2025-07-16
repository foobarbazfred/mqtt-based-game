#!/usr/bin/python3

# MQTT Game Renda OH
# PC Sample code
# Controller
# V0.01 (2025/7/16)
#

from controller  import GameController
from game_agent import GameAgent


def main():

    game_agent = GameAgent('controller')
    game_controller = GameController(game_agent)
    game_controller.main_loop()
    
    
main()
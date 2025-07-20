#!/usr/bin/python3

# MQTT Game Renda OH
# PC Sample code
# Player
# V0.01 (2025/7/16)
#

from player import GamePlayer
from game_agent import GameAgent

def main():

    game_agent = GameAgent('player')
    player_id = 'id_pc_0000'
    player_nick_name = 'i_am_p0'
    game_player = GamePlayer(game_agent, player_id, player_nick_name)
    game_player.main_loop()
    
main()
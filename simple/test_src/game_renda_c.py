#!/usr/bin/python3

from controller  import GameController
from player import GamePlayer

is_player = False
is_controller = True

if is_player:

   player_id = 'id_12234'
   player_nick_name = 'name_5963'

   game_player = GamePlayer(player_id, player_nick_name)
   game_player.main_loop()


if is_controller:

    #
    # start Game Controller
    #
    game_controller = GameController()
    game_controller.main_loop()

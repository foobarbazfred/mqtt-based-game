#!/usr/bin/python3

from controller  import GameController
from player import GamePlayer

is_player = True
is_Controller = False

if is_player:

   player_id = 'id_0001'
   player_nick_name = 'i_am_p1'

   game_player = GamePlayer(player_id, player_nick_name)
   game_player.main_loop()


if is_controller:

    #
    # start Game Controller
    #
    game_controller = GameController()
    game_controller.main_loop()

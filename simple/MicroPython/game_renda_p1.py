#
# MQTT Game Renda OH 
#  main function
#  v0.01 (2025/8/2)
#

from player import GamePlayer
from game_agent import GameAgent
from mylib import get_uniq_id

GPIO_SWITCH = 0
GPIO_SPEAKER = 16
GPIO_NEOPIXEL = 17
#NEOPIXEL_LED_SIZE = 24
NEOPIXEL_LED_SIZE = 12

def main():

    game_agent = GameAgent('player')

    player_id = get_uniq_id('pico2w_', length=8)
    player_nick_name = 'player02_5678'
    
    ui_config = {
        'GPIO_SWITCH' : GPIO_SWITCH,
        'GPIO_SPEAKER' : GPIO_SPEAKER,
        'GPIO_NEOPIXEL' : GPIO_NEOPIXEL,
        'NEOPIXEL_LED_SIZE' : NEOPIXEL_LED_SIZE
    }

    game_player = GamePlayer(game_agent, player_id, player_nick_name)
    game_player.main_loop()
    
    
main()



#
#
#
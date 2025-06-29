#
# v0.07  2025/6/29 17:00
#    refine


TOPIC_ROOT = 'game-renda'

# define topics

#
#  controller -> player
#

#
# command message for change state machine
#
TOPIC_COMMAND_CHANGE_STATE = f'{TOPIC_ROOT}/command/change-state'
#
# payload
#  { 'game_id' : <game_id>, 'next_state' : <next_state> }
#   
#   <game_id> := type(str)
#   <next_state> := type(str)
#


TOPIC_GAME_SUMMARY = f'{TOPIC_ROOT}/summary'
#
# payload
#  {
#    'game_id' : <str> 
#    'player_status' :
#        { <plyer_id> : {'click_count' : <click_count> 'nick_name' : <name>,
#            ....
#        
#     }
#  }
#


#
# not in use
#
# command message for upload players status
# controller -> player
#
#TOPIC_GAME_STATUS_REPORT = f'{TOPIC_ROOT}/command/upload-status'
#
# payload
#  { 'game_id' : <str> }
#


#
#  not in use
#  player -> controller
#

#
# join message from player
#
# TOPIC_PLAYER_JOIN = f'{TOPIC_ROOT}/player/join'
#
# payload
#  { 'player_id' : <str>, 'player_nick_name' : <str> }
#


#
# report message from player
#
TOPIC_PLAYER_REPORT = f'{TOPIC_ROOT}/player/report'
#
# payload
#  { 'player_id' : <str>, 'click_count' : <int> }
#


# not in use
#
# leave message from player
#
# TOPIC_PLAYER_LEAVE = f'{TOPIC_ROOT}/player/leave'
#
# payload
#  { 'player_id' : <str>, 'player_nick_name' : <str> }
#


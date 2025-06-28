TOPIC_BASE = 'game_renda'
# define topics
TOPIC_GAME_READY = f'{TOPIC_BASE}/command/ready'
TOPIC_GAME_COUNTDOWN_TO_START_3 = f'{TOPIC_BASE}/command/countdown/start/3'
TOPIC_GAME_COUNTDOWN_TO_START_2 = f'{TOPIC_BASE}/command/countdown/start/2'
TOPIC_GAME_COUNTDOWN_TO_START_1 = f'{TOPIC_BASE}/command/countdown/start/1'
TOPIC_GAME_START = f'{TOPIC_BASE}/command/start'
TOPIC_GAME_COUNTDOWN_TO_STOP_3 = f'{TOPIC_BASE}/command/countdown/stop/3'
TOPIC_GAME_COUNTDOWN_TO_STOP_2 = f'{TOPIC_BASE}/command/countdown/stop/2'
TOPIC_GAME_COUNTDOWN_TO_STOP_1 = f'{TOPIC_BASE}/command/countdown/stop/1'
TOPIC_GAME_STOP = f'{TOPIC_BASE}/command/stop'
TOPIC_GAME_RESULT = f'{TOPIC_BASE}/command/result'


#
# Periodic task (request status to players and report summary)
# (exec every 0.5 sec)

# controller -> player
# proc_player_status_report()
TOPIC_GAME_STATUS_REPORT = f'{TOPIC_BASE}/command/status_report'


# player -> controller
TOPIC_PLAYERS_REPORT = f'{TOPIC_BASE}/player/report'

# controller -> player
# proc_player_summary()
TOPIC_GAME_SUMMARY = f'{TOPIC_BASE}/summary'


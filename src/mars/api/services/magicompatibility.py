#!/usr/bin/env python

"""Logic behind magicompatibility's views
"""

from flask import make_response, current_app

def server_service():
    state = current_app.game_manager.get_ongoing_game_infos()
    returned_dict = {
            "PlayerCount": state.player_count,
            "Map": state.current_map,
            "PlayerList": [],
            "ServerName": state.server_name,
            "GameMode": state.game_mode
    }
    return make_response(returned_dict, 200)

def players_service():
    return make_response({'error': 'Not implemented'}, 501)

def players_all_service():
    return make_response({'error': 'Not implemented'}, 501)

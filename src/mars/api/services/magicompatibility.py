#!/usr/bin/env python

"""Logic behind magicompatibility's views
"""

from flask import make_response, current_app

def server_service():
    return make_response({
        "PlayerCount": 0,
        "Map": None,
        "PlayerList": [],
        "ServerName": current_app.game_manager.server_options.launch_options.servername,
        "GameMode": None
    }, 200)

def players_service():
    return make_response({'error': 'Not implemented'}, 501)

def players_all_service():
    return make_response({'error': 'Not implemented'}, 501)

#!/usr/bin/env python

"""Logic behind privileged commands
"""

from flask import make_response, current_app

def start_service():
    if not current_app.game_manager.get_state()['running']:
        current_app.game_manager.start()
        return make_response("Starting", 200)
    else:
        return make_response("Already running", 409)

def stop_service():
    if current_app.game_manager.get_state()['running']:
        current_app.game_manager.stop()
        return make_response("Stopping", 200)
    else:
        return make_response("Already stopped", 409)

def restart_service():
    current_app.game_manager.restart()
    return make_response("Restarting", 200)

def change_settings_service():
    pass

def change_servername_service():
    pass

def change_playlist_service():
    pass

def change_map_service():
    pass

def change_gamemode_service():
    pass

def change_numbots_service():
    pass

def change_maxplayers_service():
    pass

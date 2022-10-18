#!/usr/bin/env python

"""Logic behind privileged commands
"""

from flask import make_response, current_app

def start_service():
    if not current_app.game_manager.get_state().running:
        current_app.game_manager.start()
        return make_response("Starting", 200)
    else:
        return make_response("Already running", 409)

def stop_service():
    if current_app.game_manager.get_state().running:
        current_app.game_manager.stop()
        return make_response("Stopping", 200)
    else:
        return make_response("Already stopped", 409)

def restart_service():
    current_app.game_manager.restart()
    return make_response("Restarting", 200)

def change_settings_service(settings):
    # TODO: Refactor... Possibly need to improve the function on LaunchOptions
    settings_copy = settings.copy()
    settings_copy.setdefault('map')
    settings_copy.setdefault('servername')
    settings_copy.setdefault('gamemode')
    settings_copy.setdefault('playlist')
    settings_copy.setdefault('numbots')
    settings_copy.setdefault('maxplayers')
    settings_copy.setdefault('timelimit')
    settings_copy.setdefault('scp')
    settings_copy.setdefault('restart')
    current_app.game_manager.server_options.staging_launch_options.load_from_dict(settings_copy)
    if settings_copy['restart']:
        current_app.game_manager.restart()
    return make_response("OK", 200)

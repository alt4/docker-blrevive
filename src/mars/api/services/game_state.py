#!/usr/bin/env python

"""Logic behind game state commands
"""

from flask import make_response, current_app

def whoami_service():
    return make_response({
        "servername": current_app.game_manager.server_options.launch_options.servername,
        "port": current_app.game_manager.server_options.launch_options.port
    }, 200)

def status_service():
    return make_response(current_app.game_manager.get_state(), 200)

def current_configuration_service():
    return make_response(current_app.game_manager.server_options.launch_options.__dict__, 200)

def staging_configuration_service():
    return make_response(current_app.game_manager.server_options.staging_launch_options.__dict__, 200)
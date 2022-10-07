#!/usr/bin/env python

"""Logic behind game state commands
"""

from flask import make_response, current_app


def whoami_service():
    return make_response({
        "servername": current_app.game_manager.config['servername'],
        "port": current_app.game_manager.config['port']
    }, 200)

def status_service():
    return make_response(current_app.game_manager.get_state(), 200)

#!/usr/bin/env python

from flask_httpauth import HTTPBasicAuth
from flask import current_app

auth = HTTPBasicAuth()

@auth.verify_password
def verify(rcon_username, rcon_password):
    if not rcon_password:
        return False
    return rcon_password == current_app.game_manager.ServerOptions.RCONPassword

#!/usr/bin/env python

"""M.A.R.S. kickin' in
"""

from flask import Flask 
import flask.cli

from .routes.gamemanager import game_manager
from .routes.gamestate import game_state
from api.utils.gamehandler import BLREHandler

import os
import logging
import atexit

application = Flask(__name__)

def parse_env():
    """Parse system envvars to build the config dict"""

    config = {}
    config['debug'] = os.getenv('MARS_DEBUG')
    config['game'] = {}
    config['game']['exe'] = os.getenv('MARS_GAME_EXE')
    # https://blrevive.gitlab.io/wiki/guides/hosting/game-server/parameters.html#game-settings
    config['game']['port'] = os.getenv('MARS_GAME_PORT')
    config['game']['map'] = os.getenv('MARS_GAME_MAP')
    config['game']['servername'] = os.getenv('MARS_GAME_SERVERNAME')
    config['game']['playlist'] = os.getenv('MARS_GAME_PLAYLIST')
    config['game']['gamemode'] = os.getenv('MARS_GAME_GAMEMODE')
    config['game']['numbots'] = os.getenv('MARS_GAME_NUMBOTS')
    config['game']['maxplayers'] = os.getenv('MARS_GAME_MAXPLAYERS')
    config['game']['timelimit'] = os.getenv('MARS_GAME_TIMELIMIT')
    config['api'] = {}
    config['api']['listen_ip'] = os.getenv('MARS_API_LISTEN_IP')
    config['api']['listen_port'] = os.getenv('MARS_API_LISTEN_PORT')
    config['api']['rcon_password'] = os.getenv('MARS_API_RCON_PASSWORD')

    return config

config = parse_env()

if not config['game']['exe']:
    raise ValueError('Missing BL:RE executable')

if config['debug']: # Only checks for existence, not content, beware
    logging.basicConfig(level=logging.DEBUG)
    flask_debug = True
else:
    logging.basicConfig(level=logging.INFO)
    flask_debug = False

#flask.cli.show_server_banner = lambda *args: None
application.game_manager = BLREHandler(config=config['game'])

# Comment this if ever necessary to run tests with unclean exits
atexit.register(application.game_manager.terminate_pid)

application.register_blueprint(game_manager, url_prefix='/mars/api/admin')
application.register_blueprint(game_state, url_prefix='/mars/api/state')

application.game_manager.start()

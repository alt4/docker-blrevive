#!/usr/bin/env python

"""M.A.R.S. kickin' in
"""

from flask import Flask

from .routes.gamemanager import game_manager
from .routes.gamestate import game_state
from .routes.magicompatibility import magi_compatibility

from api.utils.gamehandler import BLREHandler

import os
import logging
import atexit

application = Flask(__name__)

def parse_env():
    """Parse system envvars to build the config dict"""

    config = {}
    config['debug'] = os.getenv('MARS_DEBUG')
    config['server'] = {}
    config['server']['exe'] = os.getenv('MARS_SERVER_EXE')
    config['server']['port'] = os.getenv('MARS_SERVER_LISTEN_PORT')
    config['game'] = {}
    config['game']['map'] = os.getenv('MARS_GAME_MAP')
    config['game']['servername'] = os.getenv('MARS_GAME_SERVERNAME')
    config['game']['playlist'] = os.getenv('MARS_GAME_PLAYLIST')
    config['game']['gamemode'] = os.getenv('MARS_GAME_GAMEMODE')
    config['game']['numbots'] = os.getenv('MARS_GAME_NUMBOTS')
    config['game']['maxplayers'] = os.getenv('MARS_GAME_MAXPLAYERS')
    config['game']['timelimit'] = os.getenv('MARS_GAME_TIMELIMIT')
    config['game']['scp'] = os.getenv('MARS_GAME_SCP')
    config['api'] = {}
    config['api']['rcon_password'] = os.getenv('MARS_API_RCON_PASSWORD')

    return config

config = parse_env()

if config['debug']: # Only checks for existence, not content, beware
    logging.basicConfig(level=logging.DEBUG)
    flask_debug = True
else:
    logging.basicConfig(level=logging.INFO)
    flask_debug = False

#flask.cli.show_server_banner = lambda *args: None
application.game_manager = BLREHandler(config=config)

# Comment this if ever necessary to run tests with unclean exits
atexit.register(application.game_manager.terminate_pid)

application.register_blueprint(game_manager, url_prefix='/api/v1/admin')
application.register_blueprint(game_state, url_prefix='/api/v1/state')
application.register_blueprint(magi_compatibility, url_prefix='/api')

application.game_manager.start()

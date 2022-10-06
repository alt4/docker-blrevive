#!/usr/bin/env python

"""M.A.R.S. kickin' in
"""

from flask import Flask 

from .api.gamemanager import game_manager
from .api.gamestate import game_state

from .utils.gamehandler import BLREHandler

app = Flask(__name__)

app.register_blueprint(game_manager, url_prefix='/mars/api/admin')
app.register_blueprint(game_state, url_prefix='/mars/api/state')
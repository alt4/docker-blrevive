#!/usr/bin/env python

"""M.A.R.S. kickin' in
"""

from flask import Flask 
import flask.cli

from .routes.gamemanager import game_manager
from .routes.gamestate import game_state

app = Flask(__name__)

flask.cli.show_server_banner = lambda *args: None

app.register_blueprint(game_manager, url_prefix='/mars/api/admin')
app.register_blueprint(game_state, url_prefix='/mars/api/state')
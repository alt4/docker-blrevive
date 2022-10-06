#!/usr/bin/env python

"""Game state polls
"""

from flask import Blueprint, request

game_state = Blueprint('game_state', __name__)

@game_state.route("/whoami", methods=['GET'])
def whoami():
    pass

@game_state.route("/status", methods=['GET'])
def status():
    pass

@game_state.route("/players", methods=['GET'])
def players():
    pass

@game_state.route("/currentmap", methods=['GET'])
def currentmap():
    pass

#!/usr/bin/env python

"""Game state polls
"""

from flask import Blueprint
from ..services.game_state import whoami_service, status_service, current_configuration_service, staging_configuration_service

game_state = Blueprint('game_state', __name__)

@game_state.route("/whoami", methods=['GET'])
def whoami():
    return whoami_service()

@game_state.route("/server", methods=['GET'])
def status():
    return status_service()

@game_state.route("/current_configuration", methods=['GET'])
def current_configuration():
    return current_configuration_service()

@game_state.route("/staging_configuration", methods=['GET'])
def staging_configuration():
    return staging_configuration_service()

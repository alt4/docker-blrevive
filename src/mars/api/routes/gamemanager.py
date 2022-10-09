#!/usr/bin/env python

"""Game manager command - priviledged
"""

from flask import Blueprint, request

from ..utils.authentication import auth
from ..services.game_manager import start_service, stop_service, restart_service, \
    change_settings_service

game_manager = Blueprint('game_manager', __name__)

# TODO? Find a cleaner way to add login than specifying it explicitely everytime

@game_manager.route("/start", methods=['GET'])
@auth.login_required
def start():
    return start_service()

@game_manager.route("/restart", methods=['GET'])
@auth.login_required
def restart():
    return restart_service()

@game_manager.route("/stop", methods=['GET'])
@auth.login_required
def stop():
    return stop_service()

@game_manager.route("/change_settings", methods=['GET', 'POST'])
@auth.login_required
def change_settings():
    data = request.args
    return change_settings_service(data)

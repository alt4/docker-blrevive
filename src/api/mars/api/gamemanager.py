#!/usr/bin/env python

"""Game manager command - priviledged
"""

from flask import Blueprint, request

game_manager = Blueprint('user_route', __name__)

@game_manager.route("/restart", methods=['GET'])
def restart():
    pass

@game_manager.route("/stop", methods=['GET'])
def stop():
    pass
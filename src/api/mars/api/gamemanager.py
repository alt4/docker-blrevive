#!/usr/bin/env python

"""Game manager command - priviledged
"""

from flask import Blueprint, request

game_manager = Blueprint('game_manager', __name__)

@game_manager.route("/restart", methods=['GET'])
def restart():
    pass

@game_manager.route("/stop", methods=['GET'])
def stop():
    pass

@game_manager.route("/change_title", methods=['POST'])
def change_title():
    pass

@game_manager.route("/change_playlist", methods=['POST'])
def change_playlist():
    pass

@game_manager.route("/change_map", methods=['POST'])
def change_map():
    pass

@game_manager.route("/change_gamemode", methods=['POST'])
def change_gamemode():
    pass

@game_manager.route("/change_numbots", methods=['POST'])
def change_numbots():
    pass

@game_manager.route("/change_maxplayers", methods=['POST'])
def change_maxplayers():
    pass

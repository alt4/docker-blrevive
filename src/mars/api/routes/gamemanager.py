#!/usr/bin/env python

"""Game manager command - priviledged
"""

from flask import Blueprint, request
from ..services.game_manager import start_service, stop_service, restart_service, \
    change_settings_service, change_servername_service, \
    change_playlist_service, change_map_service, change_gamemode_service, \
    change_numbots_service, change_maxplayers_service

game_manager = Blueprint('game_manager', __name__)

@game_manager.route("/start", methods=['GET'])
def start():
    return start_service()

@game_manager.route("/restart", methods=['GET'])
def restart():
    return restart_service()

@game_manager.route("/stop", methods=['GET'])
def stop():
    return stop_service()

@game_manager.route("/change_settings", methods=['POST'])
def change_settings():
    data = request.args
    return change_settings_service(data)

@game_manager.route("/change_servername", methods=['POST'])
def change_servername():
    data = request.args
    return change_servername_service(data)

@game_manager.route("/change_playlist", methods=['POST'])
def change_playlist():
    data = request.args
    return change_playlist_service(data)

@game_manager.route("/change_map", methods=['POST'])
def change_map():
    data = request.args
    return change_map_service(data)

@game_manager.route("/change_gamemode", methods=['POST'])
def change_gamemode():
    data = request.args
    return change_gamemode_service(data)

@game_manager.route("/change_numbots", methods=['POST'])
def change_numbots():
    data = request.args
    return change_numbots_service(data)

@game_manager.route("/change_maxplayers", methods=['POST'])
def change_maxplayers():
    data = request.args
    return change_maxplayers_service(data)

#!/usr/bin/env python

"""Compatibility interface of sorts with MagicCow's stuffs
"""

from flask import Blueprint
from ..services.magicompatibility import server_service, players_service, players_all_service

magi_compatibility = Blueprint('magi_compatibility', __name__)

@magi_compatibility.route("/server", methods=['GET'])
def server():
    return server_service()

@magi_compatibility.route("/players")
def players():
    return players_service()

@magi_compatibility.route("/players/all")
def players_all():
    return players_all_service()

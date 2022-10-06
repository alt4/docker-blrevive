#!/usr/bin/env python

from tkinter import N
from xvfbwrapper import Xvfb
import os
import pathlib
import subprocess
import logging

"""Game-handling toolbox
"""

class BLREHandler():
    def __init__(self, executable, title, playlist, gamemode, map, numbots, maxplayers):
        # Xvfb preparation for what's to come - unused since BLRE seems fine without it (for now)
        # self.vdisplay = Xvfb(width=1024, height=768, colordepth=16)
        # self.logger = logging.getLogger(__name__)
        
        # Initial settings
        self.executable = executable
        self.title = title
        self.playlist = playlist
        self.gamemode = gamemode
        self.map = map
        self.numbots = numbots
        self.maxplayers = maxplayers
        
        self.start()

    def start(self):        
        executable_path = pathlib.Path(self.executable)
        self.logger.debug('Moving to directory: {}'.format(executable_path.parent))
        os.chdir(executable_path.parent)

        command = self.__build_command()
        self.logger.debug('Attempting to spawn a new server with the following command: {}'.format(command))
        process = subprocess.run(command, shell=True, subprocess=subprocess.PIPE)
        return True

    def __build_command(self):
        "wine", "FoxGame-win32-Shipping-Patched-Server.exe server HeloDeck?Game=FoxGame.FoxGameMP_TDM?NumBots=10?port=7777"
        self.logger.debug("Preparing a command for the following args: executable={} title={} playlist={} gamemode={} map={} numbots={} maxplayers={}".format(
            self.executable,
            self.title,
            self.playlist,
            self.gamemode,
            self.map,
            self.numbots,
            self.maxplayers
        ))

        argstring = ""

        if 

        return ["wine", 
            pathlib.Path(self.executable).name,
            "server",
            argstring
        ]
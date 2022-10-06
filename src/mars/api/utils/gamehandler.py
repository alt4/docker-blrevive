#!/usr/bin/env python

# from xvfbwrapper import Xvfb
import os
import pathlib
import subprocess
import logging

"""Game-handling toolbox
"""

class BLREHandler():
    def __init__(self, config):
        # Xvfb preparation for what's to come - unused since BLRE seems fine without it (for now)
        # self.vdisplay = Xvfb(width=1024, height=768, colordepth=16)
        
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Could be interesting to let the caller decide when to start, but it might be annoying with flask
        self.start()

    def start(self):        
        command = self.__build_command()

        self.logger.debug('Attempting to spawn a new server with the following command: {}'.format(command))
        # TODO: Handle stdlog/err
        self.process = subprocess.Popen(command, cwd=pathlib.Path(self.config['exe']).parent, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return True

    def get_state(self):
        # TODO
        return {'Placeholder': "hi!"}

    def stop(self):
        self.process

    def restart(self):
        self.stop()
        self.process = None
        self.start()

    def __build_command(self):
        self.logger.debug("Preparing a command for the following args: executable={} map={} port={} servername={} playlist={} gamemode={} numbots={} maxplayers={} timelimit={}".format(
            self.config['exe'],
            self.config['port'],
            self.config['map'],
            self.config['servername'],
            self.config['playlist'],
            self.config['gamemode'],
            self.config['numbots'],
            self.config['maxplayers'],
            self.config['timelimit'],
        ))

        return ["wine", 
            pathlib.Path(self.config['exe']).name,
            "server",
            # Fasten your seatbelts
            "{map}{port}{servername}{playlist}{gamemode}{numbots}{maxplayers}{timelimit}".format(
                map=self.config['map'] if self.config['map'] else "HeloDeck",
                port="?Port={}".format(self.config['port']) if self.config['port'] else '',
                servername="?ServerName={}".format(self.config['servername']) if self.config['servername'] else '',
                playlist="?Playlist={}".format(self.config['playlist']) if self.config['playlist'] else '',
                gamemode="?Game={}".format(self.config['gamemode']) if self.config['gamemode'] else '',
                numbots="?NumBots={}".format(self.config['numbots']) if self.config['numbots'] else '',
                maxplayers="?MaxPlayers={}".format(self.config['maxplayers']) if self.config['maxplayers'] else '',
                timelimit="?TimeLimit={}".format(self.config['timelimit']) if self.config['timelimit'] else ''
            )
        ]

if __name__ == '__main__':
    # Tests, will be removed at some point. Disregard
    config = {
        "exe": "lol",
        "map": "lol",
        "port": "7777",
        "servername": "Lol",
        "playlist": "DM",
        "gamemode": "",
        "numbots": "1",
        "maxplayers": "6",
        "timelimit": "10"
    }

    logging.basicConfig(level=logging.DEBUG)

    BLREHandler(config)
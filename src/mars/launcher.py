#!/usr/bin/env python

"""Game-handling toolbox
"""

from xvfbwrapper import Xvfb
import os
import subprocess
import logging
import time
import sys

import dataclasses
from pathlib import Path


@dataclasses.dataclass
class LaunchOptions:
    """Contains game-specific options. Essentially based on MagicCow's own server_structs:
    https://github.com/MajiKau/BLRE-Server-Info-Discord-Bot/blob/master/src/classes/server_structs.py
    """
    map: str = 'HeloDeck'
    port: int = 7777
    playlist: str = None # Also changed so it doesn't default to a playlist, overriding simple map/gamemode choices
    gamemode: str = None
    numbots: int = None # Changed from Magi's to fit servers own denomination
    maxplayers: int = 16
    timelimit: int = None
    scp: int = None
    servername: str = 'MARS Managed Server'

    def __init__(self, config: dict = {}):
        super().__init__()
        if config:
            self.load_from_dict(config)

    def prepare_arguments(self):
        # Fasten your seatbelts
        return "{map}{port}{playlist}{gamemode}{numbots}{maxplayers}{timelimit}{scp}{servername}".format(
            map=self.map,
            port="?Port={}".format(self.port),
            playlist="?Playlist={}".format(self.playlist) if self.playlist else '',
            gamemode="?Game=FoxGame.FoxGameMP_{}".format(self.playlist) if self.playlist else "?Game=FoxGame.FoxGameMP_{}".format(self.gamemode) if self.gamemode else '',
            numbots="?NumBots={}".format(self.numbots) if self.numbots else '',
            maxplayers="?MaxPlayers={}".format(self.maxplayers) if self.maxplayers != 16 else '',
            timelimit="?TimeLimit={}".format(self.timelimit) if self.timelimit else '',
            scp="?SCP={}".format(self.scp) if self.scp else '',
            servername='?Servername=\"{}\"'.format(self.servername)
        )

    def load_from_dict(self, config: dict):
        self.map = config['map'] or self.map
        self.playlist = config['playlist'] or self.playlist
        self.gamemode = config['gamemode'] or self.gamemode
        self.numbots = config['numbots'] or self.numbots
        self.maxplayers = config['maxplayers'] or self.maxplayers
        self.timelimit = config['timelimit'] or self.timelimit
        self.scp = config['scp'] or self.scp
        self.servername = config['servername'] or self.servername


@dataclasses.dataclass
class ServerOptions:
    """Contains global server options such as where the game executable is located, what start arguments will be passed, etc...
    Essentially based on MagicCow's own server_structs:
    https://github.com/MajiKau/BLRE-Server-Info-Discord-Bot/blob/master/src/classes/server_structs.py
    """
    launch_options: LaunchOptions = LaunchOptions()
    server_executable: str = "BLR.exe"
    server_executable_path: Path = None

    def parse_configuration(self, config: dict):
        server_executable_path = Path("/mnt/blacklightre/Binaries/Win32", config['server']['exe'] or self.server_executable)
        if not server_executable_path.is_file():
            raise FileNotFoundError('Could not find BL:RE executable: {}'.format(server_executable_path))

        self.launch_options = LaunchOptions(config['game'])
        self.server_executable=config['server']['exe'] or self.server_executable
        self.server_executable_path=server_executable_path


class BLREHandler():
    def __init__(self, config):
        """Handler initialization

        Prepares the game start by:
            * Parsing the starting configuration
            * Making sure no other server is currently running on the same port
        """
        # Xvfb preparation for what's to come
        self.vdisplay = Xvfb(width=1024, height=768, colordepth=16)
        self.vdisplay.start()

        self.logger = logging.getLogger(__name__)
        self.logger.info("Mars is booting...")
        
        self.logger.debug("Configuration: {}".format(config))

        self.server_options = ServerOptions()
        self.server_options.parse_configuration(config)

    def ensure_alive(self):
        """Polls the subprocess for an eventual exit code, logging it if found
        """
        try:
            if not self.process.poll():
                self.logger.debug("Server's running.")
                return True
            else:
                self.logger.error("Server exited with error code {}".format(self.process.poll()))
                return False
        except AttributeError:
            self.logger.error("No known process, cannot get the state")
            return False

    def run(self):
        """Main loop, just starts the server and checks it at regular intervals
        """
        command = ["wine", 
            self.server_options.server_executable,
            "server",
            self.server_options.launch_options.prepare_arguments()
        ]

        self.logger.debug('Trying to spawn a new server with the following command: {}'.format(command))
        self.process = subprocess.Popen(command, cwd=self.server_options.server_executable_path.parent, shell=False, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # FIXME: remove DEVNULLS in favor of logging

        self.logger.info("Started a new server with PID #{}".format(self.process.pid))

        while self.ensure_alive():
            time.sleep(5)

        sys.exit(self.process.poll())


def parse_env():
    """Parse system envvars to build the config dict"""

    config = {}
    config['debug'] = os.getenv('MARS_DEBUG')
    config['server'] = {}
    config['server']['exe'] = os.getenv('MARS_SERVER_EXE')
    config['game'] = {}
    config['game']['map'] = os.getenv('MARS_GAME_MAP')
    config['game']['servername'] = os.getenv('MARS_GAME_SERVERNAME')
    config['game']['playlist'] = os.getenv('MARS_GAME_PLAYLIST')
    config['game']['gamemode'] = os.getenv('MARS_GAME_GAMEMODE')
    config['game']['numbots'] = os.getenv('MARS_GAME_NUMBOTS')
    config['game']['maxplayers'] = os.getenv('MARS_GAME_MAXPLAYERS')
    config['game']['timelimit'] = os.getenv('MARS_GAME_TIMELIMIT')
    config['game']['scp'] = os.getenv('MARS_GAME_SCP')

    return config


if __name__ == '__main__':
    config = parse_env()

    if config['debug']: # Only checks for existence, not content, beware
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    game_manager = BLREHandler(config=config)

    game_manager.run()
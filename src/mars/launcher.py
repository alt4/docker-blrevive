#!/usr/bin/env python

"""Game-handling toolbox
"""

from xvfbwrapper import Xvfb
import os
import signal
import subprocess
import logging
import time

import dataclasses
from pathlib import Path


@dataclasses.dataclass
class LaunchOptions:
    """Contains game-specific options. Essentially based on MagicCow's own server_structs:
    https://github.com/MajiKau/BLRE-Server-Info-Discord-Bot/blob/master/src/classes/server_structs.py
    """
    map: str = 'HeloDeck'
    servername: str = 'MARS Managed Server'
    gamemode: str = None
    port: int = 7777
    numbots: int = None # Changed from Magi's to fit servers own denomination
    maxplayers: int = 16
    playlist: str = None # Also changed so it doesn't default to a playlist, overriding simple map/gamemode choices
    scp: int = None
    timelimit: int = None

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
            servername="?Servername={}".format(self.servername.replace(" ", "")) # Replace is a temporary bandaid, troubleshoot later (wine or python fuckery this time?)
        )

    def load_from_dict(self, config: dict):
        self.map = config['map'] or self.map
        self.servername = config['servername'] or self.servername
        self.gamemode = config['gamemode'] or self.gamemode
        self.playlist = config['playlist'] or self.playlist
        self.numbots = config['numbots'] or self.numbots
        self.maxplayers = config['maxplayers'] or self.maxplayers
        self.timelimit = config['timelimit'] or self.timelimit
        self.scp = config['scp'] or self.scp


@dataclasses.dataclass
class ServerOptions:
    """Contains global server options such as where the game executable is located, which log/PID file will be used, etc...
    Essentially based on MagicCow's own server_structs:
    https://github.com/MajiKau/BLRE-Server-Info-Discord-Bot/blob/master/src/classes/server_structs.py
    """
    launch_options: LaunchOptions = LaunchOptions()
    server_executable: str = "BLR.exe"
    server_executable_path: Path = None
    pid_file_path: Path = None
    log_file_path: Path = None

    def parse_configuration(self, config: dict):
        server_executable_path = Path("/mnt/blacklightre/Binaries/Win32", config['server']['exe'] or self.server_executable)
        if not server_executable_path.is_file():
            raise FileNotFoundError('Could not find BL:RE executable: {}'.format(server_executable_path))

        self.server_executable=config['server']['exe'] or self.server_executable
        self.server_executable_path=server_executable_path
        self.pid_file_path=Path('/srv/mars/pid/blrevive-{}.pid'.format(config['server']['port'] or self.launch_options.port))
        self.log_file_path=Path('/srv/mars/logs/blrevive-{}.log'.format(config['server']['port'] or self.launch_options.port))


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
        self.logger.debug("Will write server's PID to: {}".format(self.server_options.pid_file_path))
        self.logger.debug("Will output server's stdout to: {}".format(self.server_options.log_file_path))

    def start(self):
        """Starts a new server process
        """

        command = ["wine", 
            self.server_options.server_executable,
            "server",
            self.server_options.launch_options.prepare_arguments()
        ]

        self.serverlog = open(self.server_options.log_file_path, 'w')

        self.logger.debug('Trying to spawn a new server with the following command: {}'.format(command))
        self.process = subprocess.Popen(command, cwd=self.server_options.server_executable_path.parent, shell=False, stdin=subprocess.DEVNULL, stdout=self.serverlog, stderr=subprocess.STDOUT)

        with open(self.server_options.pid_file_path, 'w') as pidfile:
            pidfile.write(str(self.process.pid))
            pidfile.close()

        self.logger.info("Started a new server with PID #{}".format(self.process.pid))

    def stop(self):
        """Stops the current server, **only if it is currently managed by this object**
        """
        try:
            self.process.terminate()
            self.logger.info("Sent SIGTERM to the server")
            self.serverlog.close()
            self.logger.debug("Closed the current server log file")
            self.process = None
            os.remove(self.server_options.pid_file_path)
        except AttributeError:
            self.logger.warn("Called the stop function but server isn't started, or process doesn't exist")

    def restart(self):
        """Restarts the current server.
        """
        self.stop()
        self.start()

    def terminate_pid(self):
        """Verifies if a process with a PID fitting the server configuration (same port) exists, and kill it
        Can be used even when the handler isn't managing the process, such as atexit calls
        """
        try:
            with open(self.server_options.pid_file_path, 'r') as pidfile:
                pid = int(pidfile.read())
                pidfile.close()
            self.logger.debug("Trying to terminate process with PID {}".format(pid))
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                self.logger.debug("Seems like the process was closed without cleaning its PID file (likely a crash)")
            self.logger.debug("Removing PID file")
            os.remove(self.server_options.pid_file_path)
        except FileNotFoundError:
            self.logger.debug("No PID file found, not terminating anything")

        try:
            self.serverlog.close()
        except AttributeError:
            self.logger.debug("No log file handle to close, skipping")

    def ensure_alive(self):
        """Polls the subprocess for an eventual exit code, logging it if found
        """
        try:
            if not self.process.poll():
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
        self.start()

        while self.ensure_alive():
            self.logger.debug("Server's running.")
            time.sleep(5)


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
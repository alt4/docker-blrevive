#!/usr/bin/env python

"""Collection of dataclasses 90% based on MagicCow's own server_structs
https://github.com/MajiKau/BLRE-Server-Info-Discord-Bot/blob/master/src/classes/server_structs.py
"""

from dataclasses import dataclass
from pathlib import Path

@dataclass
class ServerInfo:
    playercount: int = 0
    map: str = ''
    playerlist: 'list[str]' = None
    servername: str = ''
    gamemode: str = ''


@dataclass
class LaunchOptions:
    map: str = 'HeloDeck'
    servername: str = 'MARS Managed Server'
    gamemode: str = ''
    port: int = 7777
    numbots: int = 0 # Changed from Magi's to fit servers own denomination
    maxplayers: int = 16
    playlist: str = '' # Also changed so it doesn't default to a playlist, overriding simple map/gamemode choices
    scp: int = 0
    timelimit: int = None

    def __init__(self, config: dict = {}):
        super().__init__()
        if config:
            self.load_from_dict(config)

    def prepare_arguments(self):
        # Fasten your seatbelts
        return "{map}{port}{servername}{playlist}{gamemode}{numbots}{maxplayers}{timelimit}{scp}".format(
            map=self.map,
            port="?Port={}".format(self.port),
            servername="?Servername={}".format(self.servername),
            playlist="?Playlist={}".format(self.Playlist) if self.Playlist else '',
            gamemode="?Game={}".format(self.gamemode) if self.gamemode else '',
            numbots="?NumBots={}".format(self.numbots) if self.numbots != 0 else '',
            maxplayers="?MaxPlayers={}".format(self.maxplayers) if self.maxplayers != 16 else '',
            timelimit="?TimeLimit={}".format(self.timelimit) if self.timelimit else '',
            scp="?SCP={}".format(self.scp) if self.scp != 0 else ''
        )

    def load_from_dict(self, config: dict):
        self.map = config['map'] or self.map
        self.servername = config['servername'] or self.servername
        self.gamemode = config['gamemode'] or self.gamemode
        self.Playlist = config['playlist'] or self.playlist
        self.numbots = config['numbots'] or self.numbots
        self.maxplayers = config['maxplayers'] or self.maxplayers
        self.timelimit = config['timelimit'] or self.timelimit
        self.scp = config['scp'] or self.scp


@dataclass
class ServerOptions:
    launch_options: LaunchOptions = LaunchOptions()
    server_executable: str = "FoxGame-win32-Shipping-Patched-Server.exe"
    server_executable_path: Path = None
    pid_file_path: Path = None
    log_file_path: Path = None
    auto_restart_in_lobby: bool = False #TODO
    rcon_password: str = "MARSAdmin"

    def parse_configuration(self, config: dict):
        server_executable_path = Path("/mnt/blacklightre/Binaries/Win32", config['server']['exe'] or self.server_executable)
        if not server_executable_path.is_file():
            raise FileNotFoundError('Could not find BL:RE executable: {}'.format(server_executable_path))

        self.launch_options = LaunchOptions(config['game'])
        self.server_executable=config['server']['exe'] or self.server_executable
        self.server_executable_path=server_executable_path
        self.pid_file_path=Path('/srv/mars/pid/blrevive-{}.pid'.format(config['server']['port'] or self.launch_options.port))
        self.log_file_path=Path('/srv/mars/logs/blrevive-{}.log'.format(config['server']['port'] or self.launch_options.port))
        self.rcon_password=config['api']['rcon_password'] or self.rcon_password
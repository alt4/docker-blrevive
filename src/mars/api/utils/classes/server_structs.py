#!/usr/bin/env python

"""Collection of dataclasses 90% based on MagicCow's own server_structs
https://github.com/MajiKau/BLRE-Server-Info-Discord-Bot/blob/master/src/classes/server_structs.py
"""

from dataclasses import dataclass
from pathlib import Path

@dataclass
class ServerInfo:
    PlayerCount: int = 0
    Map: str = ''
    PlayerList: 'list[str]' = None
    ServerName: str = ''
    GameMode: str = ''


@dataclass
class LaunchOptions:
    Map: str = 'HeloDeck'
    Servername: str = 'MARS Managed Server'
    Gamemode: str = ''
    Port: int = 7777
    NumBots: int = 0 # Changed from Magi's to fit servers own denomination
    MaxPlayers: int = 16
    Playlist: str = '' # Also changed so it doesn't default to a playlist, overriding simple map/gamemode choices
    SCP: int = 0
    TimeLimit: int = None

    def __init__(self, config: dict = {}):
        super().__init__()
        if config:
            self.load_from_dict(config)

    def prepare_arguments(self):
        # Fasten your seatbelts
        return "{map}{port}{servername}{playlist}{gamemode}{numbots}{maxplayers}{timelimit}".format(
            map=self.Map,
            port="?Port={}".format(self.Port),
            servername="?ServerName={}".format(self.Servername),
            playlist="?Playlist={}".format(self.Playlist) if self.Playlist else '',
            gamemode="?Game={}".format(self.Gamemode) if self.Gamemode else '',
            numbots="?NumBots={}".format(self.NumBots) if self.NumBots != 0 else '',
            maxplayers="?MaxPlayers={}".format(self.MaxPlayers) if self.MaxPlayers != 16 else '',
            timelimit="?TimeLimit={}".format(self.TimeLimit) if self.TimeLimit else ''
        )

    def load_from_dict(self, config: dict):
        self.Map = config['map'] or self.Map
        self.Servername = config['servername'] or self.Servername
        self.Gamemode = config['gamemode'] or self.Gamemode
        self.Playlist = config['playlist'] or self.Playlist
        self.NumBots = config['numbots'] or self.NumBots
        self.MaxPlayers = config['maxplayers'] or self.MaxPlayers
        self.TimeLimit = config['timelimit'] or self.TimeLimit
        self.SCP = config['scp'] or self.SCP


@dataclass
class ServerOptions:
    LaunchOptions: LaunchOptions = LaunchOptions()
    ServerExecutable: str = "FoxGame-win32-Shipping-Patched-Server.exe"
    ServerExecutablePath: Path = None
    PidFilePath: Path = None
    LogFilePath: Path = None
    AutoRestartInLobby: bool = False #TODO
    RCONPassword: str = "MARSAdmin"

    def parse_configuration(self, config: dict):
        ServerExecutablePath = Path("/mnt/blacklightre/Binaries/Win32", config['server']['exe'] or self.ServerExecutable)
        if not ServerExecutablePath.is_file():
            raise FileNotFoundError('Could not find BL:RE executable: {}'.format(ServerExecutablePath))

        self.LaunchOptions = LaunchOptions(config['game'])
        self.ServerExecutable=config['server']['exe'] or self.ServerExecutable
        self.ServerExecutablePath=ServerExecutablePath
        self.PidFilePath=Path('/srv/mars/pid/blrevive-{}.pid'.format(config['server']['port'] or self.LaunchOptions.Port))
        self.LogFilePath=Path('/srv/mars/logs/blrevive-{}.log'.format(config['server']['port'] or self.LaunchOptions.Port))
        self.RCONPassword=config['api']['rcon_password'] or self.RCONPassword
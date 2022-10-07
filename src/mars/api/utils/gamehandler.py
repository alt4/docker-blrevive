#!/usr/bin/env python

# from xvfbwrapper import Xvfb
import os
import signal
import pathlib
import subprocess
import logging
import re

"""Game-handling toolbox
"""

class BLREHandler():
    def __init__(self, config):
        """Handler initialization

        Prepares the game start by:
            * Parsing the starting configuration
            * Making sure no other server is currently running on the same port
        """
        # Xvfb preparation for what's to come - unused since BLRE seems fine without it (for now)
        # self.vdisplay = Xvfb(width=1024, height=768, colordepth=16)

        self.logger = logging.getLogger(__name__)
        self.logger.info("Mars is booting...")
        self.config = self.__parse_config(config)
        self.logger.debug("Parsed configuration, result: {}".format(self.config))

        self.pidfilepath = pathlib.Path('/tmp/blrevive-{}.pid'.format(self.config['port']))
        self.logger.debug("Will use PID file: {}".format(self.pidfilepath))

        self.__check_for_conflicts()

    def start(self):
        """Starts a new server process
        """
        # TODO? Check for port availability?
        command = self.__build_command()

        self.logger.debug('Trying to spawn a new server with the following command: {}'.format(command))
        # TODO: Handle stdout/err
        self.process = subprocess.Popen(command, cwd=pathlib.Path(self.config['exe']).parent, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        with open(self.pidfilepath, 'w') as pidfile:
            pidfile.write(str(self.process.pid))
            pidfile.close()

        self.logger.info("Started a new server with PID #{}".format(self.process.pid))

        return self.process.pid

    def get_state(self):
        """Gets the current server state
        """
        # Ensure every values are returned, even if empty, to have a consistent json
        # TODO? Use a class instead?
        state = {
            "running": False,
            "last_exit_code": None,
            "server_match_config": None
        }
        try:
            if not self.process.poll():
                state['running'] = True
            else:
                state['running'] = False
                state['last_exit_code'] = self.process.poll()
        except AttributeError:
            self.logger.debug("No known process, cannot get the state")
            state['running'] = False
        finally:
            return state

    def stop(self):
        """Stops the current server, **only if it is currently managed by this object**
        """
        try:
            self.process.terminate()
            self.logger.info("Sent SIGTERM to the server")
            self.process = None
            os.remove(self.pidfilepath)
        except AttributeError:
            self.logger.warn("Called the stop function but server isn't started, or process doesn't exist")

    def restart(self):
        """Restarts the current server
        """
        self.stop()
        self.start()

    def terminate_pid(self):
        """Verify if a process with a PID fitting the server configuration (same port) exists, and kill it
        Can be used even when the handler isn't managing the process
        """
        try:
            with open(self.pidfilepath, 'r') as pidfile:
                pid = int(pidfile.read())
                pidfile.close()
            self.logger.debug("Trying to terminate process with PID {}".format(pid))
            os.kill(pid, signal.SIGTERM)
            self.logger.debug("Removing PID file")
            os.remove(self.pidfilepath)
        except FileNotFoundError:
            self.logger.debug("No PID file found, not terminating anything")

    def __parse_config(self, config):
        """Fill user-provided config with default values when necessary
        """
        if not config['port']:
            config['port'] = "7777"
        if not config['servername']:
            config['servername'] = "MARS Managed BLRE Server"
        return config

    def __ensure_alive_pid(self):
        """Checks if a process matching a BL:RE server exists at specified PID, returns True if that is the case
        """
        with open(self.pidfilepath, 'r') as pidfile:
            pid = int(pidfile.read())
            pidfile.close()

        self.logger.debug("Process in PID file's name: {}".format(pid))
        processes = subprocess.Popen(["ps"], stdout=subprocess.PIPE, shell=True).communicate()[0].decode().splitlines()
        self.logger.debug("Going to try and match processes with the following regex: '{}'".format("{}.*server.*Port={}".format(pid, self.config['port'])))
        regex_pid = re.compile("{}.*server.*Port={}".format(pid, self.config['port']))
        confirmed_processes = list(filter(regex_pid.search, processes))
        if confirmed_processes:
            self.logger.debug("Found the following processes that match what we're looking for (there should only be one or something is very wrong): {}".format(confirmed_processes))
            return confirmed_processes
        else:
            self.logger.debug("Found no relevant process in the system. PID file probably wasn't cleaned up.")
            return False

    def __check_for_conflicts(self):
        """Minor checks to increase probabilities BL:RE won't crash on startup
        """
        pidfiles = [filename for filename in os.listdir(self.pidfilepath.parent) if filename.startswith("blrevive-")]
        if self.pidfilepath.name in pidfiles:
            if self.__ensure_alive_pid():
                raise RuntimeError("There already is a BL:RE server running that was not properly cleaned up")
            else:
                self.logger.error("A PID file unexpectedly exists, but no process is fitting. Expect trouble.")
        elif pidfiles:
            self.logger.debug("Seems like other BL:RE servers are currently running due to these files existing: {}".format(pidfiles))
        else:
            self.logger.debug("No other PID files known")

    def __build_command(self):
        """Prepare a wine command that'll be called as a new process
        """
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

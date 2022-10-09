#!/usr/bin/env python

from xvfbwrapper import Xvfb
import os
import signal
import subprocess
import logging
import re

from .classes.server_structs import ServerOptions

"""Game-handling toolbox
"""

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

        self.__check_for_conflicts()

    def start(self):
        """Starts a new server process
        """
        # TODO? Check for port availability?
        self.logger.debug('Committing staging launch options before starting the server')
        self.server_options.commit_launch_options()

        command = ["wine", 
            self.server_options.server_executable,
            "server",
            self.server_options.launch_options.prepare_arguments()
        ]

        self.serverlog = open(self.server_options.log_file_path, 'w')

        self.logger.debug('Trying to spawn a new server with the following command: {}'.format(command))
        self.process = subprocess.Popen(command, cwd=self.server_options.server_executable_path.parent, shell=False, stdout=self.serverlog, stderr=subprocess.STDOUT)

        with open(self.server_options.pid_file_path, 'w') as pidfile:
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
            if self.server_options.launch_options == self.server_options.staging_launch_options:
                state['server_match_config'] = True
            else:
                state['server_match_config'] = False
            return state

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
        """Restarts the current server
        """
        self.stop()
        self.start()

    def terminate_pid(self):
        """Verify if a process with a PID fitting the server configuration (same port) exists, and kill it
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

    def __ensure_alive_pid(self):
        """Checks if a process matching a BL:RE server exists at specified PID, returns True if that is the case
        """
        with open(self.server_options.pid_file_path, 'r') as pidfile:
            pid = int(pidfile.read())
            pidfile.close()

        self.logger.debug("Process in PID file's name: {}".format(pid))
        processes = subprocess.Popen(["ps"], stdout=subprocess.PIPE, shell=True).communicate()[0].decode().splitlines()
        self.logger.debug("Going to try and match processes with the following regex: '{}'".format("{}.*server.*Port={}".format(pid, self.server_options.launch_options.Port)))
        regex_pid = re.compile("{}.*server.*Port={}".format(pid, self.server_options.launch_options.Port))
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
        pidfiles = [filename for filename in os.listdir(self.server_options.pid_file_path.parent) if filename.startswith("blrevive-")]
        if self.server_options.pid_file_path.name in pidfiles:
            if self.__ensure_alive_pid():
                raise RuntimeError("There already is a BL:RE server running that was not properly cleaned up")
            else:
                self.logger.error("A PID file unexpectedly exists, but no process is fitting. Expect trouble.")
        elif pidfiles:
            self.logger.debug("Seems like other BL:RE servers are currently running due to these files existing: {}".format(pidfiles))
        else:
            self.logger.debug("No other PID files known")
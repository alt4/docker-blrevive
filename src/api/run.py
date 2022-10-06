#!/usr/bin/env python

"""Launch script for the server API
"""

from mars import app
import argparse
import toml
import os
import logging

def parse_env():
    """Parse system envvars to build the config dict"""

    config = {}
    config['debug'] = os.getenv('MARS_DEBUG')
    config['game'] = {}
    config['game']['path'] = os.getenv('MARS_GAME_PATH')
    config['game']['title'] = os.getenv('MARS_GAME_TITLE')
    config['game']['playlist'] = os.getenv('MARS_GAME_PLAYLIST')
    config['game']['gamemode'] = os.getenv('MARS_GAME_GAMEMODE')
    config['game']['map'] = os.getenv('MARS_GAME_MAP')
    config['game']['numbots'] = os.getenv('MARS_GAME_NUMBOTS')
    config['game']['maxplayers'] = os.getenv('MARS_GAME_MAXPLAYERS')
    config['api'] = {}
    config['api']['enabled'] = os.getenv('MARS_API_ENABLED')
    config['api']['listen_ip'] = os.getenv('MARS_API_LISTEN_IP')
    config['api']['listen_port'] = os.getenv('MARS_API_LISTEN_PORT')
    config['api']['rcon_password'] = os.getenv('MARS_API_RCON_PASSWORD')

    return config


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Blacklight: Retribution Revive server state manager HTTP API')
    parser.add_argument('-f', '--configfile', metavar='config.toml', nargs='?',
                        default='config.toml', help='Use specified configuration file.')
    parser.add_argument('--docker', '--env', action='store_true', help='Get configuration from envvars.')

    args = parser.parse_args()
    if not (args.configfile):
        raise ValueError('"-f" cannot be empty.')

    if not args.docker:
        with open(args.configfile, 'r') as content_file:
            config = toml.loads(content_file.read())
    else:
        config = parse_env()

    if config['debug']: # Only checks for existence, not content
        logging.basicConfig(level=logging.DEBUG)
        flask_debug = True
    else:
        logging.basicConfig(level=logging.INFO)
        flask_debug = False

    logger = logging.getLogger(__name__)

    if config['api']['enabled']:
        logger.info("Starting the web API on http://{}:{}".format(config['api']['listen_ip'], config['api']['listen_port']))
        app.game_config = config['game']
        app.run(host=config['api']['listen_ip'], port=config['api']['listen_port'], debug=flask_debug)
    else:
        # Move it up top to import anyway?
        from .mars.utils.gamehandler import BLREHandler
        #todo
        # game = BLREHandler(config['game'])
        # game.start()
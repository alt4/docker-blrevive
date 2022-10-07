#!/usr/bin/env python

"""Launch script for the server API
"""

import argparse

from api import app

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Blacklight: Retribution Revive server state manager HTTP **DEV** API')
    parser.add_argument('-a', '--address', default="127.0.0.1", help="IP the server should bind to")
    parser.add_argument('-p', '--port', default="5000", help="Port the server should bind to")
    args = parser.parse_args()
    app.run(host=args.address, port=args.port, debug=True)
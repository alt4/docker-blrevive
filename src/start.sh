#!/bin/sh

gunicorn -b $MARS_API_LISTEN_IP:$MARS_API_LISTEN_PORT api
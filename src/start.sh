#!/bin/sh

gunicorn -b $MARS_API_LISTEN_IP -p $MARS_API_LISTEN_PORT api
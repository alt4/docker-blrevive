#!/bin/sh

if [ -t 0 ]; then
  echo "Please do not start the container interactively as it will cause issues with Wine. Remove -t from your command and try again."
  exit 1
fi

gunicorn -b $MARS_API_LISTEN_IP:$MARS_API_LISTEN_PORT api
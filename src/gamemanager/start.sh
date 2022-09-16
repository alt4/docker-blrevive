#!/bin/sh
Xvfb :0 -screen 0 1024x768x16 &
# I'm a hack and I'm sorry
cd /mnt/blacklightre/Binaries/Win32
DISPLAY=:0 $@
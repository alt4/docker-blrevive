#!/usr/bin/env python

from xvfbwrapper import Xvfb

"""Game-handling toolbox
"""

class BLREHandler():
    def __init__(self, config):
        self.config = config

    def start_vdisplay(self):
        self.vdisplay = Xvfb(width=1024, height=768, colordepth=16)
        self.vdisplay.start()

    def stop_vdisplay(self):
        self.vdisplay.stop()
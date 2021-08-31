#!/usr/bin/python
import sys

from curses import *

from myconstants import *
from NethackSock import *
from FramebufferParser import *
from SocketLogger import *
from DGLParser import *
from Personality import *
from Senses import *
from Console import *
from Hero import *
from Dungeon import *
from MonsterSpoiler import *
from Pathing import *
from TestBrain import *
from Cursor import *
from ItemDB import *
from Inventory import *

import gym
import nle

class Eeek:
    def __init__(self):
        # Initialize the Kernel
        Kernel()

        # Socket observers
        # SocketLogger() # This should be before other stuff for easier debugging
        self.frame_buffer = FramebufferParser()
        # DGLParser()

        # Stuff 
        Console()
        Cursor()
        Dungeon()
        Hero()
        MonsterSpoiler()
        ItemDB()
        Inventory()

        # AI
        Personality()
        Senses()
        Pathing()

        # Brains
        curBrain = TestBrain()

        Kernel.instance.Personality.setBrain(curBrain) # Default brain

    def run(self):
        env = gym.make("NetHackChallenge-v0", savedir='replays')
        obs = env.reset()
        done = False
        while not done:
            y, x = obs['tty_cursor']
            self.frame_buffer.parse(self._render(obs['tty_chars']))
            self.frame_buffer.x = x
            self.frame_buffer.y = y
            Kernel.instance.screenParsed()

            # Kernel.instance.sockRecv()

    def _render(env, obs):
        result = ''
        i = 0
        for row in obs:
            for ch in row:
                result += chr(ch)
            i += 1
            # result += '\n'
        return result


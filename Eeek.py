import Kernel
import sys

# from curses import *

from myconstants import *
# from NethackSock import *
from FramebufferParser import *
# from SocketLogger import *
# from DGLParser import *
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
        self.env = gym.make("NetHackChallenge-v0", savedir='replays')
        Kernel(self.env)

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
        sys.stdout.write("\u001b[2J\u001b[0;0H")
        while not Kernel.instance.done:
            obs = Kernel.instance.obs
            y, x = obs['tty_cursor']
            self.frame_buffer.parse(obs['tty_chars'], obs['tty_colors'])
            self.frame_buffer.x = x
            self.frame_buffer.y = y
            Kernel.instance.screenParsed()
        input(f'GAME OVER: {Kernel.instance.reward}')


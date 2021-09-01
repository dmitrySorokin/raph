import Kernel
import sys

from myconstants import *
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
            Kernel.instance.step()
        input(f'GAME OVER: {Kernel.instance.reward}')


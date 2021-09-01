#!/usr/local/bin/python3

import Kernel
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


if __name__ == '__main__':
    # Initialize the Kernel
    env = gym.make("NetHackChallenge-v0", savedir='replays')
    Kernel(silent=False)

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

    Kernel.instance.Personality.setBrain(curBrain)  # Default brain

    done = False
    reward = 0
    obs = env.reset()

    action2id = {
        chr(action.value): action_id for action_id, action in enumerate(env._actions)
    }

    while not done:
        aciton = Kernel.instance.step(obs)
        for ch in Kernel.instance.action:
            Kernel.instance.log("Sent string:" + ch + ' ' + str(type(ch)))
            Kernel.instance.log("Sent string:" + ch + ' ' + str(action2id.get(ch)))
            obs, rew, done, info = env.step(action2id.get(ch))
            reward += rew
        Kernel.instance.drawString(f"reward {reward}")
    input(f'GAME OVER: {reward}')

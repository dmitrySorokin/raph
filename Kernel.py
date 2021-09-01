import re
from FramebufferParser import *
import sys

import random


class Kernel:
    instance = None

    def __init__(self, env):
        self.signalReceivers = []
        self._file = open("logs/log.txt", "w")
        self._frames_log = open("logs/frames.txt", "w")

        Kernel.instance = self
        self.env = env
        self.obs = self.env.reset()

        self.action2id = {
            chr(action.value): action_id for action_id, action in enumerate(env._actions)
        }

        self.reward = 0
        self.done = False

        self.frame_buffer = FramebufferParser()

    def curLevel(self):
        return self.Dungeon.curBranch.curLevel

    def curTile(self):
        return self.Dungeon.curBranch.curLevel.tiles[Kernel.instance.Hero.x + Kernel.instance.Hero.y*WIDTH]

    def searchMap(self, regex):
        return re.search(regex, self.frame_buffer.mapLines())

    def searchBot(self, regex):
        return re.search(regex, self.frame_buffer.botLines())

    def searchTop(self, regex):
        return re.search(regex, self.frame_buffer.topLine())

    def top_line(self):
        return self.frame_buffer.topLine()

    def bot_line(self):
        return self.frame_buffer.botLines()

    def get_row_line(self, row):
        return self.frame_buffer.getRowLine(row)

    def map_tiles(self):
        return self.frame_buffer.mapTiles()

    def step(self):
        y, x = self.obs['tty_cursor']
        self.frame_buffer.parse(self.obs['tty_chars'], self.obs['tty_colors'])
        self.frame_buffer.x = x
        self.frame_buffer.y = y
        self.logScreen()

        self.log("Updates starting: \n\n")

        self.log("--------- SENSES --------- ")
        self.Senses.update()
        self.log("--------- DUNGEON ---------")
        self.Dungeon.update()
        self.log("-------- MESSAGES -------- ")
        self.Senses.parseMessages()
        self.log("------ PERSONALITY ------  ")
        self.Personality.nextAction()

        self.log("\n\nUpdates ended.")

    def addSignalReceiver(self, sr):
        self.signalReceivers.append(sr)

    def sendSignal(self, s, *args, **args2):
        self.log("Sending signal " + s)
        for sr in self.signalReceivers:
            sr.signal(s, *args, **args2)

    def send(self, line):
        for ch in line:
            self.log("Sent string:" + ch + ' ' + str(type(ch)))
            self.log("Sent string:" + ch + ' ' + str(self.action2id.get(ch)))
            self.obs, rew, self.done, info = self.env.step(self.action2id.get(ch))
            self.reward += rew
        Kernel.instance.drawString(f"reward {self.reward}")

    def log(self, str):
        self._file.write("%s"%str+"\n")
        self._file.flush()

    def die(self, msg):
        sys.stdout.write("\x1b[35m\x1b[3;1H%s\x1b[m\x1b[25;0f" % msg)
        self.log(msg)
        exit()

    def drawString(self, msg):
        Kernel.instance.log("Currently -> "+msg)
        sys.stdout.write("\x1b[35m\x1b[25;0H%s\x1b[m" % msg + " "*(240-len(msg)))
        sys.stdout.flush()

    def addch(self, y, x, char, c=None):
        sys.stdout.write("%s\x1b[%d;%dH%s\x1b[m" % (c and "\x1b[%dm" % c or "", y, x, char))

    def dontUpdate(self):
        self.Dungeon.dontUpdate()
        self.Personality.dontUpdate()
        self.Senses.dontUpdate()

    def logScreen(self):
        for y in range(0, HEIGHT):
            self._frames_log.write("\n")
            for x in range(0, WIDTH):
                if y == HEIGHT-1 and x > WIDTH-5:
                    break
                self._frames_log.write(self.frame_buffer.screen[x+y*WIDTH].char)
        if Kernel.instance.Dungeon.curBranch:
            self._frames_log.write(str(Kernel.instance.curTile().coords()))
            self._frames_log.write("\n"+str(self.frame_buffer.y)+","+str(self.frame_buffer.x))
        self._frames_log.flush()

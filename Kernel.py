import re
from myconstants import *
from TermColor import *
import sys

import random

class Kernel:
    instance = None
    def __init__(self):
        self.signalReceivers = []
        self._file = open("logs/log.txt", "wa")
        self.observers = []

        Kernel.instance = self

    def curLevel(self):
        return self.Dungeon.curBranch.curLevel
    def curTile(self):
        return self.Dungeon.curBranch.curLevel.tiles[Kernel.instance.Hero.x + Kernel.instance.Hero.y*WIDTH]

    def searchMap(self, regex):
        return re.search(regex, self.FramebufferParser.mapLines())

    def searchBot(self, regex):
        return re.search(regex, self.FramebufferParser.botLines())

    def searchTop(self, regex):
        return re.search(regex, self.FramebufferParser.topLine())

    def handleStartup(self):
        Kernel.instance.send("\x1b")
        pass

    def screenParsed(self):
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

    def addObserver(self, observer):
        self.observers.append(observer)

    def send(self, line):
        self.log("Sent string:" + line)
        return self.NethackSock.send(line)

    def sockRecv(self, line):
        self.log('sockRecv ' + line)
        for observer in self.observers:
            observer.parse(line)

    def log(self, str):
        self._file.write("%s"%str+"\n")
        self._file.flush()

    def die(self, msg):
        sys.stdout.write("\x1b[35m\x1b[3;1H%s\x1b[m\x1b[25;0f" % msg)
        self.log(msg)
        self.NethackSock.die()
        exit()

    def drawString(self, msg):
        Kernel.instance.log("Currently -> "+msg)
        sys.stdout.write("\x1b[35m\x1b[25;0H%s\x1b[m" % msg + " "*(240-len(msg)))
        sys.stdout.flush()

    def addch(self, y, x, char, c=None):
        sys.stdout.write("%s\x1b[%d;%dH%s\x1b[m" % (c and "\x1b[%dm" % c or "", y, x, char))

    def setPause(self, to):
        self.log("Setting pause to %s" % str(to))
        self.NethackSock.paused = to
    def paused(self):
        return self.NethackSock.paused

    def dontUpdate(self):
        self.Dungeon.dontUpdate()
        self.Personality.dontUpdate()
        self.Senses.dontUpdate()


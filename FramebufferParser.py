import sys
import time
import re
from Tile import *
from SignalReceiver import *
from SocketObserver import *
from Kernel import *
from EeekObject import *
from TermColor import *

from myconstants import *


class FBTile:
    def __init__(self):
        self.char = ' '
        self.color = TermColor()
        self.marked = None

    def set(self, char, color):
        self.char = char
        self.color = color


class FramebufferParser(SignalReceiver, SocketObserver, EeekObject):
    def __init__(self):
        EeekObject.__init__(self)
        SignalReceiver.__init__(self)
        SocketObserver.__init__(self)

        self.gameStarted = False
        self.screen = []

        self.state = ""
        self.y = 0
        self.x = 0

        self.herox = 0
        self.heroy = 0

        self.color = TermColor()

        self._file = open("logs/frames.txt", "w")
        self.firstParse = True
        self.last = ""

        for x in range(0, WIDTH*HEIGHT):
            self.screen.append(FBTile())

        self.ansi =\
            {
                "\xf0"     : "ignore",
                "\x1b[m"   : "reset color",
                "\x1b[0m"  : "reset color",
                "\x1b[1m"  : "bold",
                "\x1b[7m"  : "reverse",
                "\x1b[?47l": "ignore",
                "\x1b[?47h": "ignore",
                "\x1b[?1l" : "ignore",
                "\x1b8"    : "ignore",
                "\x1b7"    : "ignore",
                "\xff\xfcc": "ignore",
                "\xfa"     : "ignore",
                "\x00"     : "ignore",
                "\x08"     : "backspace",
                "\x0a"     : "LF",
                "\x0a"     : "LF",
                "\x0d"     : "CR",
                "\x1b(B"   : "ignore",
                "\x1b)0"   : "ignore",
                "\x1b>"    : "ignore",
                "\x1b[?1l" : "ignore",
                "\x1b[H"   : "home",
                "\x1b[J"   : "clear to end of screen",
                "\x1b[0J"  : "clear to end of screen",
                "\x1b[1J"  : "clear to beginning",
                "\x1b[2J"  : "clear screen",
                "\x1b[K"   : "clear to end of line",
                "\x1b[A"   : "up",
                "\x1b[B"   : "down",
                "\x1b[C"   : "right",
                "\x1b[D"   : "left",
                "\x1by"    : "ignore",
            }
        for x in range(ord(' '), ord('~')+1):
            self.ansi[chr(x)] = "print"

    def mapTiles(self):
        return self.screen[WIDTH:-WIDTH*2]

    def getChars(self):
        return "".join(x.char for x in self.screen)

    def mapLines(self):
        return "".join(x.char for x in self.screen[WIDTH:-2*WIDTH])

    def topLine(self):
        return "".join(x.char for x in self.screen[:WIDTH])

    def botLines(self):
        return "".join(x.char for x in self.screen[22*WIDTH:])

    def getRowLine(self, row):
        if row < 1 or row > 24:
            return ""
        return "".join(x.char for x in self.screen[(row-1)*WIDTH:row*WIDTH])

    def printChar(self, char):
        cur = self.screen[self.x + self.y*WIDTH]
        cur.set(char, self.color.copy())
        self.x = self.x+1

    def log(self, line):
        self._file.write(line+"\n")
        self._file.flush()

    def parse(self, line):
        self.x, self.y = 0, 0


        self.last = line

        self.state = ""

        for char in line:
            self.state = self.state + char
            if self.state in self.ansi:
                action = self.ansi[self.state]
                if action == "print":
                    self.printChar(char)
                elif action == "reset color":
                    self.color = TermColor()
                elif action == 'CR':
                    self.x = 0
                elif action == 'backspace':
                    self.x = self.x - 1
                elif action in ('LF', "down"):
                    self.y = self.y + 1
                elif action == "up":
                    self.y = self.y - 1
                elif action == "left":
                    self.x = self.x - 1
                elif action == "right":
                    self.x = self.x + 1
                elif action == 'ignore':
                    pass
                elif action == "home":
                    self.x = 0
                    self.y = 0
                elif action == "clear to end of screen":
                    for i in range(self.x + self.y * WIDTH, WIDTH * HEIGHT):
                        self.screen[i].set(' ', TermColor())
                elif action == "clear to end of line":
                    for i in range(self.x + self.y * WIDTH, WIDTH * (self.y + 1)):
                        self.screen[i].set(' ', TermColor())
                elif action == "clear to beginning":
                    for i in range(self.x + self.y * WIDTH, 0, -1):
                        self.screen[i].set(' ', TermColor())
                elif action == "clear screen":
                    for i in range(0, HEIGHT*WIDTH):
                        self.screen[i].set(' ', TermColor())
                elif action == "bold":
                    self.color.bold = True
                elif action == "reverse":
                    self.color.reverse = True

                self.state = ""
                if self.x >= WIDTH:
                    self.x = 0
                    self.y = self.y + 1
                if self.y >= HEIGHT:
                    self.y = HEIGHT - 1
                continue

            match = re.match("\x1b\[(\d+);(\d+)H", self.state)
            if match:
                self.y = int(match.group(1)) - 1
                self.x = int(match.group(2)) - 1
                self.state = ""
                continue

            if len(self.state)>10:
                Kernel.instance.log("Couldn't parse ANSI: %s\nBuffer was: %s" % (line, self.state))
                Kernel.instance.die("Couldn't parse ANSI")
                return

            match = re.match("\x1b\[(\d+)m", self.state)
            if match:
                col = int(match.group(1))
                if col>=30 and col<=37:
                    self.color.fg = col
                elif col>=40 and col<=47:
                    self.color.bg = col
                else:
                    Kernel.instance.die("Invalid color: %d" % col)
                self.state = ""
                continue

        if True:
            for y in range(0, HEIGHT):
                for x in range(0, WIDTH):
                    cur = self.screen[x+y*WIDTH]
                    sys.stdout.write("\x1b[%dm\x1b[%d;%dH%s" % (cur.color.fg, y+1, x+1, cur.char))
            sys.stdout.flush()

        self.logScreen()

    def logScreen(self):
        for y in range(0, HEIGHT):
            self._file.write("\n")
            for x in range(0, WIDTH):
                if y == HEIGHT-1 and x > WIDTH-5:
                    break
                self._file.write(self.screen[x+y*WIDTH].char)
        if Kernel.instance.Dungeon.curBranch:
            self._file.write(str(Kernel.instance.curTile().coords()))
            self._file.write("\n"+str(self.y)+","+str(self.x))
        self._file.flush()

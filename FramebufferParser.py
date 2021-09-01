import sys
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


class FramebufferParser:
    def __init__(self):

        self.gameStarted = False
        self.screen = []

        self.state = ""
        self.y = 0
        self.x = 0

        self.herox = 0
        self.heroy = 0

        self.color = TermColor()

        self.firstParse = True

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

    def parse(self, chars, colors):
        self.x, self.y = 0, 0

        self.state = ""

        for char, color in zip(chars.reshape(-1), colors.reshape(-1)):
            char = chr(char)

            TTY_BRIGHT = 8

            is_bold = bool(color & TTY_BRIGHT)
            color = 30 + int(color & ~TTY_BRIGHT)

            self.color = TermColor(color)
            self.color.bold = is_bold
            self.printChar(char)
            if self.x >= WIDTH:
                self.x = 0
                self.y = self.y + 1
            if self.y >= HEIGHT:
                self.y = HEIGHT - 1

        for y in range(0, HEIGHT):
            for x in range(0, WIDTH):
                cur = self.screen[x+y*WIDTH]
                sys.stdout.write("\x1b[%dm\x1b[%d;%dH%s" % (cur.color.fg, y+1, x+1, cur.char))
        sys.stdout.flush()

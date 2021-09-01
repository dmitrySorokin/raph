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
        self.screen = [FBTile() for _ in range(WIDTH * HEIGHT)]
        self.y = 0
        self.x = 0
        self.color = TermColor()
        self.top_line = None
        self.bot_line = None

    def mapTiles(self):
        return self.screen[WIDTH:-WIDTH*2]

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

    def parse(self, obs):
        self.x, self.y = 0, 0
        self.top_line = obs['message']

        chars, colors = obs['tty_chars'], obs['tty_colors']

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

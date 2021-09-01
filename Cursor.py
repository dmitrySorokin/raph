from EeekObject import *
from myconstants import *
from Kernel import *


class Cursor(EeekObject):
    def __init__(self):
        EeekObject.__init__(self)
        self.started = True
        self.y = 0
        self.x = 0

    def start(self):
        self.started = True
        self.y = Kernel.instance.Hero.y
        self.x = Kernel.instance.Hero.x

        Kernel.instance.log("Cursor starts at (%d,%d)" % (self.y, self.x))

    def draw(self):
        Kernel.instance.stdout("\x1b[%d;%df" % (self.y+2, self.x+1))

    def input(self, char):
        if char not in ['y','u','h','j','k','l','b','n','.']:
            return
        if char == '.':
            pass
        else:
            dir = directions[char]
            self.y = self.y + dir[0]
            self.x = self.x + dir[1]
            Kernel.instance.drawString(str(Kernel.instance.Dungeon.tile(self.y, self.x)))
            self.draw()

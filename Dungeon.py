from Kernel import *
from EeekObject import *
from Branch import *

class Dungeon(EeekObject):
    def __init__(self):
        EeekObject.__init__(self)

        self.branches = [Branch("Main"), Branch("Mines"), Branch("Sokoban"), Branch("Quest"), Branch("Gehennom"), Branch("Planes"), Branch("Unknown")]
        self.curBranch = None
        self.updateNext = False

    def tile(self, y, x):
        return self.curBranch.curLevel.tiles[x + y*WIDTH]

    def update(self):
        if not self.updateNext:
            self.updateNext = True
            return

        # I think we can set Hero's y,x here - should be no --More--'s and such
        # TODO: I should keep track of where Hero -should- be (Hero.move()) and at least try \x12 if no match
        Kernel.instance.log("Setting Hero to (%d,%d)" % (Kernel.instance.frame_buffer.x, Kernel.instance.frame_buffer.y-1))
        Kernel.instance.Hero.x = Kernel.instance.frame_buffer.x
        Kernel.instance.Hero.y = Kernel.instance.frame_buffer.y-1
        if self.curBranch:
            Kernel.instance.log("Curtile is now (%s)" % str(Kernel.instance.curTile()))

        if not self.curBranch or self.curBranch.curLevel.dlvl != self.dlvl:
            self.curBranch = self.guessBranch()
            Kernel.instance.sendSignal("new_dlvl")

        self.curBranch.update()

    def guessBranch(self):
        if self.dlvl < 2 or (self.dlvl > WHEREIS_MINES[-1] and self.dlvl < WHEREIS_GEHENNOM[0]):
            return [branch for branch in self.branches if branch.name == "Main"][0]
        else:
            return [branch for branch in self.branches if branch.name == "Unknown"][0]

    def dontUpdate(self):
        Kernel.instance.log("Someone told the Dungeon not to update this tick! Probably Senses")
        self.updateNext = False

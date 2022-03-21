from nethack_raph.Branch import Branch
from nethack_raph.myconstants import DUNGEON_WIDTH
from nethack_raph.myconstants import WHEREIS_MINES, WHEREIS_GEHENNOM


class Dungeon:
    def __init__(self, kernel):
        self.kernel = kernel
        self.branches = [
            Branch("Main", kernel),
            Branch("Mines", kernel),
            Branch("Sokoban", kernel),
            Branch("Quest", kernel),
            Branch("Gehennom", kernel),
            Branch("Planes", kernel),
            Branch("Unknown", kernel)
        ]
        self.curBranch = None
        self.dlvl = -1

    def tile(self, y, x):
        return self.curBranch.curLevel.tiles[x + y * DUNGEON_WIDTH]

    def update(self, chars, glyphs):
        if not self.curBranch or self.curBranch.curLevel.dlvl != self.dlvl:
            self.curBranch = self.guessBranch()

        self.curBranch.update(chars, glyphs)

    def guessBranch(self):
        if self.dlvl < 2 or (self.dlvl > WHEREIS_MINES[-1] and self.dlvl < WHEREIS_GEHENNOM[0]):
            return [branch for branch in self.branches if branch.name == "Main"][0]
        else:
            return [branch for branch in self.branches if branch.name == "Unknown"][0]

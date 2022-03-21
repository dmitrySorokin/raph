from nethack_raph.Level import *


class Branch:
    def __init__(self, name, kernel):
        self.name = name
        self.levels = []
        self.curLevel = None
        self.kernel = kernel

    def update(self, chars, glyphs):
        if not self.curLevel or self.curLevel.dlvl != self.kernel().dungeon.dlvl:
            result = [level for level in self.levels if level.dlvl == self.kernel().dungeon.dlvl]
            if len(result) > 1:
                self.kernel().die("Found several levels with current dlvl in same branch: %s. This shouldn't happen before I reach mines" % str(result))
            if result:
                self.curLevel = result[0]
            else:
                self.levels.append(Level(self.kernel, self.kernel().dungeon.dlvl))
                self.curLevel = self.levels[-1]

        self.curLevel.update(chars, glyphs)

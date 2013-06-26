from Level import *

class Branch:
    def __init__(self, name):
        self.name = name
        self.levels = []
        self.curLevel = None

    def update(self):
        if not self.curLevel or self.curLevel.dlvl != Kernel.instance.Dungeon.dlvl:
            result = [level for level in self.levels if level.dlvl == Kernel.instance.Dungeon.dlvl]
            if len(result) > 1:
                Kernel.instance.die("Found several levels with current dlvl in same branch: %s. This shouldn't happen before I reach mines" % str(result))
            if result:
                self.curLevel = result[0]
            else:
                self.levels.append(Level(Kernel.instance.Dungeon.dlvl))
                self.curLevel = self.levels[-1]


        self.curLevel.update()

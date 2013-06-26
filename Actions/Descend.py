from Kernel import *

class Descend:
    def __init__(self):
        self.goal    = None
        self.path    = None
        self.descend = False

    def can(self):
        if Kernel.instance.curTile().glyph == '>':
            Kernel.instance.log("We're standing on '>'. Let's descend!")
            self.descend = True
            self.goal = False
            return True

        self.descend = False

        if not self.goal:
            Kernel.instance.log("Finding '>' ..")
            stairs = Kernel.instance.curLevel().find({'glyph': '>'})
            for stair in stairs: # Grammar <3
                Kernel.instance.log("Found one (%s)" % str(stair))
                path = Kernel.instance.Pathing.path(end=stair)
                if path:
                    Kernel.instance.log("Path: %s" % path)
                    self.goal = stair
                    self.path = path
                    return True
        else:
            path = Kernel.instance.Pathing.path(end=self.goal)
            if path:
                self.path = path
                return True
        return False

    def execute(self):
        if self.descend:
            Kernel.instance.Hero.descend()
            self.path = None
            self.goal = None
        else:
            Kernel.instance.log("Going towards stairs")

            self.path.draw(color=COLOR_BG_GREEN)
            Kernel.instance.Hero.move(self.path[-2].tile)

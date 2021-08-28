from Kernel import *
import time

class SearchSpot:
    def __init__(self):
        self.goal = None

    def can(self):
        if self.goal and (self.goal.searched or self.goal.walkable or self.goal.glyph == '+'):
            Kernel.instance.log("Done searching hotspot.")
            self.goal = None

        #                 #
        # This will get ###@
        #                 #
        unsearched = Kernel.instance.curTile().adjacent({'walkable': False, 'searched': False})
        if len(unsearched) > 4 and len(Kernel.instance.curTile().straight({'walkable': True})) == 1:
            for tile in Kernel.instance.curTile().neighbours():
                if tile.glyph in ['+']: # So it won't search on "###@]  "
                    return False
            self.goal = sorted(unsearched, lambda x,y: x.searches-y.searches)[0]
            return True
        return False

    def execute(self):
        Kernel.instance.log("Searching..")
        Kernel.instance.drawString("Searching hotspot (%s)" % self.goal)
        Kernel.instance.Hero.search()
        if self.goal.searches >= 10:
            self.goal.searched = True
            self.goal = None

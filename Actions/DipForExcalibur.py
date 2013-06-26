from Kernel import *

class DipForExcalibur:
    def __init__(self):
        self.path = None
        self.dip = False

    def can(self):
        if Kernel.instance.curTile().glyph == '}':
            excal = Kernel.instance.Inventory.search({'appearance': 'long sword'}, getFirst=True)
            if excal:
                self.item = excal
                self.path = None
                self.dip = True
                return True

        if self.path and self.path.isWalkable():
            return True

        if Kernel.instance.Hero.xp >= 5 and not Kernel.instance.ItemDB.find({'appearance': 'Excalibur'}):
            for tile in Kernel.instance.curLevel().find({'glyph': '{'}):
                path = Kernel.instance.Pathing.path(end=tile)
                if path:
                    self.path = path
        else:
            self.path = None
            return False

        return self.path and True or False

    def execute(self):
        if self.dip:
            Kernel.instance.log("Dipping for excalibur.")
            Kernel.instance.Hero.dip( self.item )
        else:
            self.path.draw(color=COLOR_GREEN)
            Kernel.instance.log("Walking towards a fountain.")
            Kernel.instance.Hero.move(self.path[-2].tile)

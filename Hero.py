from Kernel import *
from EeekObject import *


class Hero(EeekObject):
    def __init__(self):
        EeekObject.__init__(self)

        self.x = None
        self.y = None
        self.beforeMove = None
        self.tmpCount = 0

        self.blind = False
        self.legShape = True

        self.inBearTrap = False
        self.inPit = False
        self.isEngulfed = False
        self.isPolymorphed = False

        self.hanger = None
        self.have_food = True

        self.lastActionedTile = None # I sersiouly need to #enhance my english skills :'(

    def coords(self):
        return (self.y, self.x)

    def attack(self, tile):
        dir = Kernel.instance.Pathing.getDirection(tile)
        Kernel.instance.drawString("Attacking -> %s (%s)" % (dir, tile))
        Kernel.instance.send("F"+dir)

    def move(self, tile):
        if self.beforeMove == (self.x,self.y) and self.tmpCount < 5 and not (self.inBearTrap or self.inPit):
            Kernel.instance.log("Hero asked to move, but I still havn't moved after last update, ignoring this")
            self.tmpCount = self.tmpCount + 1
        else:
            if self.beforeMove != (self.x, self.y):
                self.inBearTrap = False
                self.inPit      = False
            else:
                if self.tmpCount > 3:
                    if not tile.glyph:
                        Kernel.instance.log("Made a door at %s" % tile)
                        tile.glyph = '-'
                        tile.color = TermColor(33, 0, False, False)
                        Kernel.instance.sendSignal("interrupt_action")

            dir = Kernel.instance.Pathing.getDirection(tile)
            Kernel.instance.drawString("Walking -> %s (%s)" % (dir, tile))

            self.beforeMove = (self.x,self.y)
            self.tmpCount   = 0

            Kernel.instance.NethackSock.s.send(dir)

    def descend(self):
        Kernel.instance.log("Hero is descending..")
        Kernel.instance.send(">")
        Kernel.instance.dontUpdate()

    def open(self, tile):
        dir = Kernel.instance.Pathing.getDirection(tile)
        Kernel.instance.log("Hero is opening a door..")
        Kernel.instance.send("o%s" % dir)
        self.lastActionedTile = tile

    def kick(self, tile):
        dir = Kernel.instance.Pathing.getDirection(tile)
        Kernel.instance.log("Hero is kicking a door..")
        Kernel.instance.send("\x04%s" % dir)

    def search(self, times=2):
        Kernel.instance.send("%ds" % times)
        for neighbour in Kernel.instance.curTile().neighbours():
            neighbour.searches = neighbour.searches + 1
            if neighbour.searches == Kernel.instance.curLevel().maxSearches:
                neighbour.searched = True

    def eat(self):
        Kernel.instance.log("Hero::eat")
        Kernel.instance.send("e")

    def canPickupHeavy(self):
        # for poly and stuff
        return False

    def canOpen(self, tile):
        return not tile.shopkeepDoor and tile.is_door and (tile.locked or Kernel.instance.Hero.legShape) and tile.isAdjacent(Kernel.instance.curTile())

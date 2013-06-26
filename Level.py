from Kernel import *
from Tile import *

class Level:
    def __init__(self, dlvl):
        Kernel.instance.log("Making a level")

        self.dlvl = dlvl
        self.branchname = Kernel.instance.Dungeon.curBranch.name
        self.tiles = []
        self.special = None
        self.explored = False
        self.maxSearches = 10

        for y in range(0, 21):
            for x in range(0,80):
                self.tiles.append(Tile(y, x, self))

        Kernel.instance.log("Made a Level() with dlvl: %d in branch %s" % (self.dlvl, self.branchname))

    def find(self, args):
        return [tile for tile in self.tiles if tile.find(args)]
    def findAttackableMonsters(self):
        return [tile for tile in self.tiles if tile.monster and tile.monster.isAttackable()]
    def findUnidentifiedItems(self):
        ret = []
        for tile in self.tiles:
            if tile.items:
                if [item for item in tile.items if not item.appearance]:
                    ret.append(tile)
        return ret
    def findDoors(self):
        return [tile for tile in self.tiles if tile.glyph == ']']

    def update(self):
        FBTiles = Kernel.instance.FramebufferParser.mapTiles()
        if len(FBTiles) != len(self.tiles):
            Kernel.instance.die("Amount of tiles in mapTiles() or Level() is wrong.")

        heroLast = Kernel.instance.curTile()
        for x in range(0, len(self.tiles)):
            if self.tiles[x].appearance() != FBTiles[x].char:
                tmp = self.tiles[x].appearance()
                Kernel.instance.log("\n   <--- %s\n   ---> %s" % (str(self.tiles[x].appearance()), str(FBTiles[x].char)))
                self.tiles[x].setTile(FBTiles[x].char, FBTiles[x].color)
                if not (self.tiles[x].isHero() or self.tiles[x].coords() == heroLast.coords()):
                    Kernel.instance.log("\n   <!!! %s(%s)\n   !!!> %s" % (tmp, str(self.tiles[x].coords()), str(FBTiles[x].char)))
                    self.explored = False

        for tile in Kernel.instance.curTile().neighbours():
            if tile.appearance() == ' ' and tile.walkable:
                Kernel.instance.log("Setting walkable to False because I think this is rock (%s)" % tile)
                tile.walkable = False

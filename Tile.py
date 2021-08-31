from Item      import *
from Monster   import *
from TermColor import *
from Kernel    import *
from Findable  import *


class Tile(Findable):
    dngFeatures = ['.', '}', '{', '#', '<', '>', '+', '^', '|', '-', '~', ' ']
    dngItems    = ['`', '0', '*', '$', '_', '[', '%', ')', '(', '/', '?', '!', '"', '=', '+', '\\']
    dngMonsters = list(map(chr, range(ord('a'), ord('z')+1))) + \
                       list(range(ord('A'), ord('Z')+1)) + \
                       list(range(ord('1'), ord('5')+1)) + \
                        ['@', "'", '&', ';', ':']
    walkables    = {'.': 1,
                    '}': 1,
                    '{': 1,
                    '#': 1,
                    '<': 1,
                    '>': 1,
                    '^': 100,
                    ' ': 1}  #glyph: weight

    def __init__(self, y, x, level):
        Findable.__init__(self)

        self.y = y
        self.x = x
        self.level = level

        self.glyph = None
        self.color = TermColor()

        self.explored = False
        self.items = []
        self.monster = None

        self.walkable = True

        self.searches = 0
        self.searched = False

        self.inShop = False

        self.locked = False
        self.shopkeepDoor = False
        self.is_door = False

    def coords(self):
        return self.y, self.x

    def setTile(self, glyph, color):
        self.monster = None
        self.is_door = glyph == '+'

        # fix for mimic monster
        glyph = 'm' if glyph == ']' else glyph

        if glyph in Tile.dngFeatures:
            self.glyph = glyph
            self.color = color

            self.explored = self.explored or (glyph != ' ')

            if self.items:
                Kernel.instance.log("Removing items on %s because I only see a dngFeature-tile" % str(self.coords()))
                self.items = []

            if glyph not in Tile.walkables.keys() and not self.isDoor():
                Kernel.instance.log("Setting %s to unwalkable." % self)
                self.walkable = False
            if glyph in Tile.walkables.keys() and glyph not in [' ']:
                self.walkable = True
            #Kernel.instance.log("Found feature: %s, Color: %s, at (%d,%d). Tile is now: %s" % (glyph, str(color), self.y, self.x, str(self)))

        elif glyph in Tile.dngItems:
            it = Item(None, glyph, color)
            if not self.items:
                Kernel.instance.log("Added item(%s) to tile(%s)" % (str(it), str(self)))
                self.items.append(it)
            else:
                self.items[0] = it

            if glyph == '0':
                self.walkable = False
            else:
                self.walkable = True
            #Kernel.instance.log("Found item: %s, Color: %s, at (%d,%d). Tile is now: %s" % (str(it), str(color), self.y, self.x, str(self)))

        elif self.coords() == Kernel.instance.curTile().coords():
            self.explored = True
            self.walkable = True

            # Might cause some trouble
            # TODO: Write comments that actually explains problems (No idea why I said the above, and no idea what the below does.. :) 
            if not self.isWalkable():
                self.walkable = True
                self.glyph = None

        elif glyph in Tile.dngMonsters:
            self.monster  = Monster(glyph, color)
            self.walkable = True
            if self.glyph == '+':
                if Kernel.instance.Dungeon.tile(self.y-1, self.x).glyph == '|':
                    self.glyph = '-'
                else:
                    self.glyph = '|'
                self.color = TermColor(33, 0, False, False)

            #Kernel.instance.log("Found monster:%s, Color: %s, at (%d,%d). Tile is now: %s" % (str(self.monster), str(color), self.y, self.x, str(self)))
        else:
            Kernel.instance.die("Couldn't parse tile: " + glyph)

    def appearance(self):
        if self.monster:
            return self.monster.glyph
        elif self.items:
            return self.items[-1].glyph
        else:
            return self.glyph

    def isDoor(self):
        return (self.glyph == '-' or self.glyph == '|') and self.color.getId() == COLOR_BROWN

    def isWalkable(self): #TODO: Shops might be good to visit sometime ..:)
#        if not self.adjacent({'explored': True}):
#            return False
        if not self.glyph:
            return not self.monster and self.walkable
        else:
            if self.isDoor():
                return not self.monster and True
            return not self.monster and self.glyph in Tile.walkables.keys() and self.walkable

    def walkableNeighbours(self):
        ret = []

        for neighbour in self.neighbours():
            if neighbour.isWalkable() and not (neighbour.isDoor() or self.isDoor()):
                ret.append(neighbour)
                continue
            if (self.isDoor() or neighbour.isDoor()) and (self.x==neighbour.x or self.y==neighbour.y) and neighbour.isWalkable():
                ret.append(neighbour)
                continue
        return ret

    def isAdjacent(self, other):
        for neighbour in self.neighbours():
            if neighbour == other:
                return True
        return False

    def straight(self, find=None):
        ret = []
        for x, y in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            if x + self.x < 0 or x + self.x >= DUNGEON_WIDTH or y + self.y < 0 or y + self.y >= DUNGEON_HEIGHT:
                continue
            tile = self.level.tiles[(x + self.x) + (y + self.y) * WIDTH]
            if find is None or tile.find(find):
                ret.append(tile)
        return ret

    def adjacent(self, find):
        return [tile for tile in self.neighbours() if tile.find(find)]

    def neighbours(self):
        ret = []
        for x in range(-1,2):
            for y in range(-1,2):
                if x+self.x<0 or x+self.x>WIDTH-1 or y+self.y<0 or y+self.y>HEIGHT-4 or (x==0 and y==0):
                    continue
                tile = self.level.tiles[x+self.x + (y+self.y)*WIDTH]
                ret.append(tile)
        return ret

    def isHero(self):
        return self.coords() == Kernel.instance.curTile().coords()

    def tilesFromCurrent(self):
        return (abs(Kernel.instance.Hero.x-self.x) + abs(Kernel.instance.Hero.y-self.y))

    def __str__(self):
        return "(%s,%s)->g:%s, c:(%s), e:%s, @:%s, m:(%s), i:(%s) w:%s(is:%s) sea:%s" % tuple(map(str, (self.y, self.x, self.glyph, self.color, self.explored, self.isHero(), self.monster, map(str, self.items), self.walkable, self.isWalkable(), self.searches)))

    def __eq__(self, other):
        return self.coords() == other.coords()

    def __ne__(self, other):
        return self.coords() != other.coords()

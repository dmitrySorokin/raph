from EeekObject import *
from Tile import *
import sys

class Pathing(EeekObject):
    def __init__(self):
        EeekObject.__init__(self)

    def path(self, start=None, end=None, find=None, max_g=None):
        if not start:
            start = Kernel.instance.curTile()
        if end:
            self.end = end
            if not end.isWalkable():
                Kernel.instance.die("Asked for unwalkable square")
                return None
            elif end == start:
                Kernel.instance.die("end == start in Pathing.path()")
                return None
        else:
            self.end = None
            if not find:
                Kernel.instance.die("No end or find in path()\n  Start:%s\n  End:%s" % (str(start), str(end)))

        Kernel.instance.log("Finding path from\n    st:%s\n    en:%s\n    fi:%s" % (str(start), str(end), str(find)))

        open   = [self.createNode(start, 0)]
        closed = []

        while open:
            # Find the most promising square
            current = open[0]
            for x in open:
                if x.f()<current.f():
                    current = x

            if self.end:
                if current.tile == self.end:
                    return current

            if find:
                if current.tile.find(find):
                    return current

            if max_g and current.g >= max_g:
                return None
            # Switch it over to closed
            open.remove(current)
            closed.append(current)

            # For each of its walkable neighbours:
            for neighbour in current.tile.walkableNeighbours():
                # Ignore it if it's already in closed
                if [x for x in closed if x.tile == neighbour]:
                    continue

                neighbourNode = self.createNode(neighbour, current)
                if self.end:
                    if neighbourNode.tile == self.end:
                        return neighbourNode

                if find:
                    if neighbourNode.tile.find(find):
                        return neighbourNode

                openNode = None
                for n in open:
                    if n.tile == neighbour:
                        openNode = n
                        break

                # Add to open if it's not already in it
                if not openNode:
                    open.append(neighbourNode)
                else:
                    # If it is, and G is better: swaptime!
                    if openNode.g > neighbourNode.g:
                        open.remove(openNode)
                        open.append(neighbourNode)

        Kernel.instance.log("open is now empty. Did not find anything in Pathing")
        return None

    def createNode(self, tile, parent):
        tmp = TileNode(tile, parent)
        if parent and tile.glyph:
            if tile.glyph in Tile.walkables.keys():
                tmp.g = parent.g + Tile.walkables[tile.glyph]
            else:
                tmp.g = parent.g + 1
        else:
            tmp.g = 0


        if self.end:
            tmp.h = abs(tile.x-self.end.x) + abs(tile.y-self.end.y)
        else:
            tmp.h = 0
        return tmp

    def getDirection(self, tile):
        if abs(Kernel.instance.curTile().y - tile.y) > 1 or abs(Kernel.instance.curTile().x - tile.x) > 1:
            Kernel.instance.die("Asked for directions to a nonadjacent tile: %s" % tile)
        if Kernel.instance.curTile().y <  tile.y and Kernel.instance.curTile().x <  tile.x: return 'n'
        if Kernel.instance.curTile().y <  tile.y and Kernel.instance.curTile().x == tile.x: return 'j'
        if Kernel.instance.curTile().y <  tile.y and Kernel.instance.curTile().x >  tile.x: return 'b'
        if Kernel.instance.curTile().y == tile.y and Kernel.instance.curTile().x <  tile.x: return 'l'
        if Kernel.instance.curTile().y == tile.y and Kernel.instance.curTile().x >  tile.x: return 'h'
        if Kernel.instance.curTile().y >  tile.y and Kernel.instance.curTile().x <  tile.x: return 'u'
        if Kernel.instance.curTile().y >  tile.y and Kernel.instance.curTile().x == tile.x: return 'k'
        if Kernel.instance.curTile().y >  tile.y and Kernel.instance.curTile().x >  tile.x: return 'y'

class TileNode:
    def __init__(self, tile, parent):
        self.tile   = tile
        self.parent = parent

        self.g = 0
        self.h = 0

    def f(self):
        return self.g+self.h

    def draw(self, color=41):
        a = self
        while a.parent != 0:
            sys.stdout.write("\x1b[%dm\x1b[%d;%dH%s\x1b[m" % (color, a.tile.y+2, a.tile.x+1, a.tile.appearance()))
            a = a.parent
        sys.stdout.flush()

    def isWalkable(self):
        a = self
        while a.parent != 0:
            if not a.tile.isWalkable():
                return False
            a = a.parent
        return True

    def __getitem__(self, i):
        reverse = False
        if i < 0:
            i = abs(i)
            reverse = True
        if len(self) < i:
            raise IndexError

        if reverse:
            toReturn = len(self)-i
        else:
            toReturn = i

        count = 0
        a = self
        while a.parent != 0:
            if count == toReturn:
                break
            a = a.parent
            count = count + 1
        return a

    def __len__(self):
        count = 1
        a = self
        while a.parent != 0:
            a = a.parent
            count = count + 1
        return count

    def __str__(self):
        ret = str(self.tile.coords())
        a = self
        while a.parent != 0:
            a = a.parent
            ret = ret + ",(" + str(a.tile.coords()) +")"
        return ret

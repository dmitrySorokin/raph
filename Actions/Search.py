from Kernel import *
import time


class Search:
    def __init__(self):
        self.path    = None
        self.walkto  = False
        self.goal    = False
        self.search  = False

    def can(self):
        # FIXME: INFINITE RECURSION HERE
        if self.goal and self.goal.searched:
            Kernel.instance.log("Searched enough here. Let's move on")
            self.walkto = None
            self.goal = None

        if self.walkto and not self.walkto.isWalkable():
            self.walkto = None
            self.goal = None
            self.search = False

        if not self.walkto:
            Kernel.instance.log("Finding possible searchwalktos")
            searchwalktos = Kernel.instance.curLevel().find({'isWalkable': False, 'searched': False})
            if searchwalktos:
                best = None
                for tile in searchwalktos:
                    if not tile.glyph in ['|', '-', ' ']:
                        continue
                    neighbours = tile.adjacent({'explored': True, 'walkable': True, 'monster': None})
                    if neighbours:
                        if (best and tile.tilesFromCurrent() < best[2]) or not best:
                            best = (tile, neighbours, neighbours[0].tilesFromCurrent())
                            continue

                if best:
                    Kernel.instance.log("Best searchspot: (%s)" % str(map(str, best)))
                    self.goal = best[0]
                    bestNeighbour = (best[1][0], 0)
                    for neighbour in best[1]:
                        count = len([x for x in neighbour.adjacent({'searched': False})])
                        if count > bestNeighbour[1]:
                            bestNeighbour = (neighbour, count)
                    self.walkto = bestNeighbour[0]

            if self.goal and self.goal.isAdjacent(Kernel.instance.curTile()) and self.goal.searches < Kernel.instance.curLevel().maxSearches:
                Kernel.instance.log("Searching tile (%s)" % str(self.walkto))
                self.search = True
                return True

        if self.walkto == Kernel.instance.curTile():
            Kernel.instance.log("Searching tile (%s)" % str(self.walkto))
            self.search = True
            return True

        elif self.walkto:
            Kernel.instance.log("Making a path to our walkto.")
            self.path = Kernel.instance.Pathing.path(end=self.walkto)
            if self.path:
                Kernel.instance.log("Found a path.")
                return True
            else:
                Kernel.instance.log("Recursing Search.can()..")
                self.walkto = None
                self.goal = None
                self.path = None
                return self.can()
        Kernel.instance.curLevel().maxSearches = Kernel.instance.curLevel().maxSearches + 5
        return False

    def execute(self):
        if self.search:
            Kernel.instance.Hero.search()
            self.search = False
        else:
            Kernel.instance.log("Going towards searchspot")

            self.path.draw(color=COLOR_BG_YELLOW)

            myPath = self.path[-2]
            myPath.parent = 0
            Kernel.instance.Hero.move(myPath.tile)
            Kernel.instance.sendSignal('interrupt_action', self)

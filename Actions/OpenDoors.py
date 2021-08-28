from Kernel import *

class OpenDoors:
    def __init__(self):
        self.path = None
        self.goal = None

    def can(self):

        if self.goal:
            if Kernel.instance.Hero.canOpen(self.goal):
                return True

        Kernel.instance.log("Checking for adjacent doors..")
        doors = Kernel.instance.curTile().adjacent({'glyph': '+'})
        for door in doors:
            if Kernel.instance.Hero.canOpen(door):
                self.goal = door
                return True

        self.path = None
        self.goal = None

        Kernel.instance.log("Looking for any doors on level..")

        doors = Kernel.instance.curLevel().findDoors()
        for door in doors:
            for adjacent in door.walkableNeighbours():
                if not adjacent.explored:
                    continue
                tmp = Kernel.instance.Pathing.path(end=adjacent, max_g=self.path and self.path.g or None)
                if tmp and (self.path == None or self.path.g > tmp.g):
                    self.path = tmp

        return self.path and True or False

    def execute(self):
        if self.goal:
            if self.goal.locked:
                Kernel.instance.Hero.kick(self.goal)
            else:
                Kernel.instance.Hero.open(self.goal)
            self.goal = None
        else:
            self.path.draw(color=COLOR_BG_CYAN)
            Kernel.instance.Hero.move(self.path[-2].tile)
            Kernel.instance.sendSignal("interrupt_action", self)

    def interrupt_action(self, who):
        if who != me:
            self.path = None
            self.goal = None



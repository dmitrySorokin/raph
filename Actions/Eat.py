import Kernel

from Kernel import *
from Pathing import TileNode
from SignalReceiver import SignalReceiver


class Eat():
    def __init__(self):
        self.in_position = False
        self.path = None
        self.adj = None

    def can(self):
        self.in_position = False
        self.path = None
        self.adj = None

        if Kernel.instance.Hero.hanger == 'Satiated':
            return False

        # if Kernel.instance.Hero.hanger not in ['Hungry', 'Weak', 'Fainting']:
        #     return False

        # if Kernel.instance.Hero.have_food:
        #     return True

        Kernel.instance.log("Checking for adjacent food.." + str(Kernel.instance.Hero.hanger))

        if Kernel.instance.Hero.can_eat(Kernel.instance.curTile()):
            self.in_position = True
            Kernel.instance.log('curr is food')
            return True

        foods = [neib for neib in Kernel.instance.curTile().neighbours() if Kernel.instance.Hero.can_eat(neib)]
        for food in foods:
            self.adj = food
            return True

        Kernel.instance.log("Looking for any foods on level..")

        foods = Kernel.instance.curLevel().find_food()
        for food in foods:
            for adjacent in food.walkableNeighbours():
                if not adjacent.explored:
                    continue
                tmp = Kernel.instance.Pathing.path(end=adjacent, max_g=self.path and self.path.g or None)
                if tmp and (self.path is None or self.path.g > tmp.g):
                    self.path = tmp
        return self.path is not None

    def execute(self):
        if self.in_position:
            Kernel.instance.Hero.eat()
            Kernel.instance.sendSignal("interrupt_action", self)
        elif self.adj:
            Kernel.instance.Hero.move(self.adj)
            Kernel.instance.log('adj ' + str(self.adj))
            Kernel.instance.log('adj ' + str(Kernel.instance.curTile()))
            Kernel.instance.log(self.adj.isWalkable())
            Kernel.instance.sendSignal("interrupt_action", self)
        else:
            Kernel.instance.log(self.path)
            Kernel.instance.Hero.move(self.path[-2].tile)
            Kernel.instance.sendSignal("interrupt_action", self)


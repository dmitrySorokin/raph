from Kernel import *
from Pathing import TileNode


class Eat:
    def __init__(self):
        self.path = None
        self.goal = None

    def can(self):
        return False
        if Kernel.instance.Hero.hanger is not None:
            return True

    def execute(self):
        Kernel.instance.Hero.eat()

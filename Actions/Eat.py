from Kernel import *
from Pathing import TileNode


class Eat:
    def __init__(self):
        self.path = None
        self.goal = None

    def can(self):
        if Kernel.instance.Hero.hanger in ['Hungry', 'Weak', 'Fainting'] and Kernel.instance.Hero.have_food:
            return True

    def execute(self):
        Kernel.instance.Hero.eat()

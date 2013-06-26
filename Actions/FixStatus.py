from Kernel import *

class FixStatus:
    def __init__(self):
        pass

    def can(self):
        return Kernel.instance.Hero.blind or Kernel.instance.Hero.isPolymorphed

    def execute(self):
        Kernel.instance.Hero.search(5)

from Kernel import *

class RestoreHP:
    def __init__(self):
        pass

    def can(self):
        if Kernel.instance.Hero.curhp <= (Kernel.instance.Hero.maxhp/2):
            return True

    def execute(self):
        Kernel.instance.log("Searching for 10 turns becuase my HP is low")
        Kernel.instance.Hero.search(10)

from SignalReceiver import *

from RandomWalk      import *
from Explore         import *
from AttackMonster   import *
from OpenDoors       import *
from GetPhatz        import *
from Descend         import *
from Search          import *
from SearchSpot      import *
from FixStatus       import *
from RestoreHP       import *
from DipForExcalibur import *

class Brain(SignalReceiver):
    def __init__(self, name):
        SignalReceiver.__init__(self)

        self.name = name
        Kernel.instance.Personality.brains.append(self)

    def __str__(self):
        return "Brain(%s)" % self.name

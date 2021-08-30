from SignalReceiver import *

from Actions.RandomWalk import *
from Actions.Explore import *
from Actions.AttackMonster import *
from Actions.OpenDoors import *
from Actions.GetPhatz import *
from Actions.Descend import *
from Actions.Search import *
from Actions.SearchSpot import *
from Actions.FixStatus import *
from Actions.RestoreHP import *
from Actions.DipForExcalibur import *
from Actions.Eat import *


class Brain(SignalReceiver):
    def __init__(self, name):
        SignalReceiver.__init__(self)

        self.name = name
        Kernel.instance.Personality.brains.append(self)

    def __str__(self):
        return "Brain(%s)" % self.name

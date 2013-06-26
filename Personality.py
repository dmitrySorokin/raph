from Kernel import *
from EeekObject import *
from SignalReceiver import *

import random
import re

class Personality(EeekObject,SignalReceiver):
    def __init__(self):
        EeekObject.__init__(self)
        SignalReceiver.__init__(self)

        self.updateNext = False
        self.brains = []

    def nextAction(self):
        if self.updateNext:
            Kernel.instance.log("\n---- Personality ----)")
            self.curBrain.executeNext()
        else:
            self.updateNext = True

    def setBrain(self, brain):
        self.curBrain = brain
        Kernel.instance.log("Setting brain to %s" % str(brain))

    def dontUpdate(self):
        Kernel.instance.log("Someone told the Personality not to update this tick! Probably Senses")
        self.updateNext = False


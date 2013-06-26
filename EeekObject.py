from Kernel import *

class EeekObject:
    def __init__(self):
        Kernel.instance.__dict__.__setitem__(self.__class__.__name__, self)
        Kernel.instance.log("Initialized %s" % self.__class__)

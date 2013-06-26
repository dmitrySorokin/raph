from Kernel import *

class SocketObserver:
    def __init__(self):
        Kernel.instance.addObserver(self)

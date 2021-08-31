from SocketObserver import *
from EeekObject import *

class SocketLogger(SocketObserver, EeekObject):
    def __init__(self):
        EeekObject.__init__(self)
        SocketObserver.__init__(self)
        self.log = open("logs/socklog.txt", 'w')
    def parse(self, line):
        self.log.write(line+"\n\n")
        self.log.flush()

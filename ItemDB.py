from EeekObject import *

class ItemDB(EeekObject):
    def __init__(self):
        EeekObject.__init__(self)
        self.items = []

    def find(self, what):
        return [item for item in self.items if item.find(what)]

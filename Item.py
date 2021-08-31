from Findable import *

class Item(Findable):
    CURSED      = 0
    UNCURSED    = 1
    BLESSED     = 2
    UNKNOWNBUC  = 3

    def __init__(self, name, glyph, color, heavy=False):
        Findable.__init__(self)

        self.name = name
        self.qty        = 1
        self.enchants   = 0
        self.buc        = Item.UNKNOWNBUC

        self.slot       = None
        self.page       = None

        self.glyph      = glyph
        self.color      = color
        self.heavy      = heavy or self.glyph in ['0']

    def __str__(self):
        return "?:%s, g:%s, c:%s" % tuple(map(str, (self.name, self.glyph, self.color)))

    def isHeavy(self):
        return self.glyph in ['`', '0']

    def canPickup(self):
        return self.glyph not in ['_', '\\']

    def identified(self, id):
        self.name = id

    def is_food(self):
        return self.glyph == '%' and self.name != 'corpse'

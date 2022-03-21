from nethack_raph.Findable import *
from nethack_raph.glossaries import MONSTERS_GLOSSARY, ITEMS_TO_THROW, LAUNCHERS, MISSILES


class Item(Findable):
    CURSED = 0
    UNCURSED = 1
    BLESSED = 2
    UNKNOWNBUC = 3

    bad_effects = ['mimic', 'poisonous', 'hallucination', 'stun', 'die', 'acidic', 'lycanthropy', 'slime',
                   'petrify', 'aggravate']

    ambivalent_effects = ['speed toggle']  # can be either good or bad, depending on the circumstances

    good_effects = ['cure stoning', 'reduce confusion', 'reduce stunning',
                    'heal', 'cold resistance', 'disintegration resistance', 'fire resistance',
                    'poison resistance', 'shock resistance', 'sleep resistance', 'gain level',
                    'teleport control', 'gain telepathy', 'increase intelligence', 'polymorphing',
                    'increase strength', 'increase energy', 'teleportitis', 'invisibility'
                    ]

    item_glyp_ranges = { # TODO: refactor
        'corpse': (1144, 1524),
        'weapon': (1907, 1976),
        'armor': (1977, 2055),
        'ring': (2056, 2083),
        'amulet': (2084, 2094),
        'tool': (2095, 2144),
        'food': (2145, 2177),
        'potion': (2178, 2203),
        'scroll': (2204, 2245),
        'spell_book': (2246, 2288),
        'wand': (2289, 2315),
        'gold_piece': (2316, 2316),
        'gem': (2317, 2352),
    }

    def __init__(self, name, char, glyph, kernel):
        Findable.__init__(self)

        self.name = name
        self.qty = 1
        self.enchants = 0
        self.buc = Item.UNKNOWNBUC

        self.char = char
        self.glyph = glyph
        self.kernel = kernel

        self.corpse = False
        self.turn_of_death = -1000
        self.is_food = self.check_if_food()

        self.item_type = None
        for k, v in Item.item_glyp_ranges.items():
            if v[0] <= self.glyph <= v[1]:
                self.item_type = k
                break
        if glyph in ITEMS_TO_THROW:
            self.item_type = 'projective'
        if glyph in LAUNCHERS:
            self.item_type = 'missile'
        if glyph in MISSILES:
            self.item_type = 'missile'

    def __str__(self):
        return "?:%s, ch:%s, g:%s" % tuple(map(str, (self.name, self.char, self.glyph)))

    def identified(self, id):
        self.name = id

    def check_if_food(self):
        if self.char != '%': return False
        if 1144 <= self.glyph <= 1524:  # corpse
            self.corpse = MONSTERS_GLOSSARY[self.glyph - 1144]['name']
            monster_corpse = MONSTERS_GLOSSARY[self.glyph - 1144]['corpse']

            if monster_corpse['cannibal'] and self.kernel().hero.race in (None, monster_corpse['cannibal']):
                # cannibalism. If we doesn't know the race, it is cannibalism for any monster that can be cannibalised
                self.kernel().log("%s is not an edible corpse." % self)
                return False

            if any([key in monster_corpse for key in Item.bad_effects + Item.ambivalent_effects]):
                self.kernel().log("%s is not an edible corpse." % self)
                return False

            else:
                self.kernel().log("%s is an edible corpse." % self)
                return True

        elif 2152 <= self.glyph <= 2155:  # glob (acidic)
            self.kernel().log("%s is glob (inedible)" % self)
            return False

        else:
            self.kernel().log("%s is food" % self)
            return True

    def is_tainted(self):
        tainted = bool(self.corpse) and self.kernel().hero.turns - self.turn_of_death >= 30
        return tainted

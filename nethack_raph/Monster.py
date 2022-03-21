from nethack_raph.glossaries import MONSTERS_GLOSSARY


class Monster:
    peacefuls_monster_glyphs = {
        (267, 267),  # Shopkeeper
        (270, 270),  # Oracle
        (271, 271),  # Aligned priest
        (278, 279),  # Watchman and Watch captain
        (367, 380),  # Quest guardian
        (342, 354),  # Quest leader
    }

    passive_monster_glyphs = {
        6,    # acid blob
        27,   # gas spore
        28,   # floating eye
        55,   # blue jelly
        56,   # spotted jelly
        156,  # brown mold
        157,  # yellow mold
        158,  # green mold
        159,  # red mold
    }

    explosive_monster_glyphs = {
        27,   # gas spore
    }

    guard_glyphs = {
        268
    }

    def __init__(self, char, glyph, kernel):
        self.char = char
        self.glyph = glyph
        self.name = "unknown"
        self.is_statue = False
        self.spoiler = {}
        self.kernel = kernel

        self.pet = 381 <= self.glyph <= 761
        self.is_monster = self.glyph < 381 or self.glyph in (762, 1906)  # invisible and mimic
        self.respect_elbereth = MONSTERS_GLOSSARY.get(self.glyph, {}).get('elbereth', 1)
        self.peaceful = any([l <= self.glyph <= r for l, r in Monster.peacefuls_monster_glyphs])
        self.passive = self.glyph in Monster.passive_monster_glyphs
        self.explosive = self.glyph in Monster.explosive_monster_glyphs
        self.guard = self.glyph in Monster.guard_glyphs
        self.range_attack = False
        self.is_attackable = self.is_monster and not self.peaceful and not self.passive and not self.guard

    def __str__(self):
        return "n:%s, ch:%s, g:%s, o:%s" % tuple(map(str, [self.name, self.char, self.glyph, self.spoiler]))

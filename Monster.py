from Kernel import *

class Monster:
    peacefuls = [
        ['@', COLOR_WHITE],       # shk
        ['@', COLOR_BRIGHT_BLUE], # oracle
        ['@', COLOR_GRAY],        # watchmen
        ['@', COLOR_GREEN],       # watch captain I think
        ['e', COLOR_BLUE],        # floating eye I think
    ]

    def __init__(self, glyph, color):
        self.glyph = glyph
        self.color = color
        self.name = "unknown"
        self.spoiler = {}

        # Exceptions
        if glyph == 'I':
            return
        if glyph == 'm' and color.getId() == 34:
            self.name = "mimic"
            return

        # ret = Kernel.instance.MonsterSpoiler.fromGlyphColor(glyph, color.getId())

        # if len(ret) == 1:
        #     (self.name, self.spoiler) = ret[0]
        #     Kernel.instance.log("Got %s" % str([self.name, self.spoiler]))
        # elif len(ret) > 1:
        #     Kernel.instance.log("Got several monsters with g:%s c:%s (%s)" % (glyph, str(color), str(ret)))
        # elif glyph != 'I':
        #     Kernel.instance.die("Could not find monster with g:%s c:%s" % (glyph, str(color)))

    def isAttackable(self):
        for peaceful in Monster.peacefuls:
            if self.glyph == peaceful[0] and self.color.getId() == peaceful[1]:
                Kernel.instance.log("%s is not attacakble." % self)
                return False
        Kernel.instance.log("%s is attackable")
        return True

    def __str__(self):
        return "n:%s, g:%s, c:%s, o:%s" % tuple(map(str, [self.name, self.glyph, self.color, self.spoiler]))

import inspect

from Kernel import *
from EeekObject import *

class Senses(EeekObject):
    def __init__(self):
        EeekObject.__init__(self)
        self.messages = []
        self.updateNext = True

        self.events = {
            "(needs food, badly!|feel weak now\.|feel weak\.)":              ['is_weak'],
            "There is a staircase (down|up) here":                           ['is_staircase_here'],
            "Your (right|left) leg is in no shape":                          ['leg_no_shape'],
            "Your leg feels somewhat better":                                ['leg_feels_better'],
            "You see here":                                                  ['found_items'],
            "Things that are here":                                          ['found_items'],
            "There are (several|many) objects here":                         ['found_items'],
            "There's some graffiti on the floor here":                       ['graffiti_on_floor'],
            "You read: (.*?)":                                               ['graffiti_on_floor'],
            "Velkommen, [^,]+!":                                                     ['shop_entrance'],
            "There is an open door here":                                    ['open_door_here'],
            "There is a bear trap here|You are caught in a bear trap":       ['found_beartrap'],
            "You feel more confident in your ([^ ]+) ":                      ['skill_up'],
            "You feel quick":                                                ['gain_instrinct', 'fast'],
            "You are momentarily blinded by a flash of light":               ['blinded'],
            "You are still in a pit|You fall into a pit":                    ['fell_into_pit'],
            "You are caught in a bear trap|A bear trap closes on your foot": ['stepped_in_beartrap'],
            "Click! You trigger":                                            ['trigger_trap'],
            "There is a magic trap here":                                    ['found_trap', 'magic'],
            "There is a falling rock trap|A trap door in the ceiling opens": ['found_trap', 'rock'],
            "There is an arrow trap":                                        ['found_trap', 'arrow'],
            "A board beneath you squeaks loudly":                            ['found_trap', 'squeek'],
            "This door is locked":                                           ['locked_door'],
            "Closed for inventory":                                          ['shopkeep_door'],
            "You get expelled":                                              ['got_expelled'],
            "You return to (human|) form":                                   ['no_poly'],
            "There is a teleportation trap here":                            ['found_trap', 'teleport'],
            r".* eat it\? \[ynq\] \(n\)":              ['eat_it'],
            "You see no door there.": ['no_door']
        }


    def update(self):
        if Kernel.instance.Hero.isEngulfed and Kernel.instance.searchTop("You destroy the (.+)"):
            self.no_poly()

        if Kernel.instance.searchTop("You die") >= 0:
            Kernel.instance.die("You died :(")

        if Kernel.instance.searchBot("the Werejackal"):
            Kernel.instance.Hero.isPolymorphed = True

        top = Kernel.instance.FramebufferParser.topLine().replace("--More--", "")
        self.messages = self.messages + top.strip().split("  ")
        Kernel.instance.log(str(self.messages))

        match = Kernel.instance.searchTop("(.+) engulfs you")
        if match:
            self.got_engulfed(match)

        match = Kernel.instance.searchTop("Call a (.+) potion")
        if match:
            self.call_potion(match)

        if Kernel.instance.searchTop("--More--"):
            Kernel.instance.log("Found --More-- (%s)" % Kernel.instance.FramebufferParser.topLine())
            Kernel.instance.send(" ")
            Kernel.instance.dontUpdate()

        if Kernel.instance.FramebufferParser.getRowLine(2).find("--More--") >= 0:
            Kernel.instance.log("Stupid graffiti ..")
            Kernel.instance.send(" ")
            Kernel.instance.dontUpdate()

        match = Kernel.instance.searchTop("(Illegal objects|Weapons|Armor|Rings|Amulets|Tools|Comestibles|Potions|Scrolls|Spellbooks|Wands|Coins|Gems|Boulders/Statues|Iron balls|Chains|Venoms)       ")
        if match:
            Kernel.instance.log("Inventory is open.")
            Kernel.instance.Inventory.parseFrame(match)
            Kernel.instance.dontUpdate()

        if Kernel.instance.searchTop("Things that are here:"):
            Kernel.instance.log("Found some items. (Row 3)")
            Kernel.instance.send("    ")
            Kernel.instance.dontUpdate()

        elif Kernel.instance.FramebufferParser.getRowLine(3).find("Things that are here:") >= 0:
            self.messages.append("Things that are here:")
            Kernel.instance.log("Found some items (row 3).")
            Kernel.instance.send("    ")
            Kernel.instance.dontUpdate()

        if Kernel.instance.searchTop("Really attack"):
            Kernel.instance.log("Asked if I really want to attack.")
            Kernel.instance.send("y")
            Kernel.instance.dontUpdate()

        if Kernel.instance.searchTop("In what direction?"):
            Kernel.instance.log("Getting rid if 'In what direction?' prompt")
            Kernel.instance.send("\x1b")
            Kernel.instance.dontUpdate()

        match = Kernel.instance.searchTop("What do you want to eat\? \[(.*) or \?\*\]")
        if match:
            self.eat(match)

        if Kernel.instance.searchTop("\? \[(.*?)\]"):
            Kernel.instance.log("Found a prompt we can't handle: %s" % Kernel.instance.FramebufferParser.topLine())
            Kernel.instance.send(" ")
            Kernel.instance.dontUpdate()

        match = Kernel.instance.searchBot("Dlvl:(\d+)\s*\$:(\d+)\s*HP:(\d+)\((\d+)\)\s*Pw:(\d+)\((\d+)\)\s*AC:(\d+)\s*HD:(\d+)\s*T:(\d+)")
        # if match:
        #     (Kernel.instance.Dungeon.dlvl, Kernel.instance.Hero.gold, Kernel.instance.Hero.curhp, Kernel.instance.Hero.maxhp, Kernel.instance.Hero.curpw, Kernel.instance.Hero.maxpw, Kernel.instance.Hero.ac, Kernel.instance.Hero.hd, Kernel.instance.turns) = map(int, match.groups())
        #     Kernel.instance.log('hui')
        match = Kernel.instance.searchBot("Dlvl:(\d+)\s*\$:(\d+)\s*HP:(\d+)\((\d+)\)\s*Pw:(\d+)\((\d+)\)\s*AC:(\d+)\s*Xp:(\d+)\/(\d+)\s*T:(\d+)\s([a-zA-Z]+)")
        match_hanger = Kernel.instance.searchBot("Dlvl:(\d+)\s*\$:(\d+)\s*HP:(\d+)\((\d+)\)\s*Pw:(\d+)\((\d+)\)\s*AC:(\d+)\s*Xp:(\d+)\/(\d+)\s*T:(\d+)")

        if match:
            (Kernel.instance.Dungeon.dlvl, Kernel.instance.Hero.gold, Kernel.instance.Hero.curhp, Kernel.instance.Hero.maxhp, Kernel.instance.Hero.curpw, Kernel.instance.Hero.maxpw, Kernel.instance.Hero.ac, Kernel.instance.Hero.xp, Kernel.instance.Hero.xp_next, Kernel.instance.turns, Kernel.instance.Hero.hanger) = map(int, match.groups()[:-1]) + [match.groups()[-1]]
        elif match_hanger:
            (Kernel.instance.Dungeon.dlvl, Kernel.instance.Hero.gold, Kernel.instance.Hero.curhp, Kernel.instance.Hero.maxhp, Kernel.instance.Hero.curpw, Kernel.instance.Hero.maxpw, Kernel.instance.Hero.ac, Kernel.instance.Hero.xp, Kernel.instance.Hero.xp_next, Kernel.instance.turns) = map(int, match_hanger.groups())
        else:
            Kernel.instance.die('not matched' + Kernel.instance.FramebufferParser.botLines())

        match = Kernel.instance.searchBot("(\w+) the \w+.*?St:([^ ]+)\s+Dx:(\d+)\s+Co:(\d+)\s+In:(\d+)\s+Wi:(\d+)\s+Ch:(\d+)\s+(\w+)\s+S:(\d+)")
        if match:
            (Kernel.instance.Hero.name, Kernel.instance.Hero.str, Kernel.instance.Hero.dex, Kernel.instance.Hero.con, Kernel.instance.Hero.int, Kernel.instance.Hero.wis, Kernel.instance.Hero.cha, Kernel.instance.Hero.align, Kernel.instance.score) = match.groups()

        if Kernel.instance.searchBot("Blind"):
            Kernel.instance.Hero.blind = True
        else:
            Kernel.instance.Hero.blind = False

    def no_poly(self):
        Kernel.instance.Hero.isPolymorphed = False

    def got_expelled(self):
        Kernel.instance.log("Got expelled. Phew!")
        Kernel.instance.Hero.isEngulfed = False
    def got_engulfed(self, match):
        Kernel.instance.log("We just got engulfed. This will confuze me a whole lot :(")
        Kernel.instance.Hero.isEngulfed = True

    def shopkeep_door(self):
        door = [tile for tile in Kernel.instance.curTile().neighbours() if tile.is_door][0]
        door.shopkeepDoor = True

    def locked_door(self):
        if Kernel.instance.Hero.lastActionedTile and Kernel.instance.Hero.lastActionedTile.is_door:
            Kernel.instance.Hero.lastActionedTile.locked = True

    def found_trap(self, type):
        Kernel.instance.log("I found a trap. Setting glyph to ^")
        Kernel.instance.curTile().glyph = '^'

    def fell_into_pit(self):
        Kernel.instance.log("I fell into a pit :(")
        Kernel.instance.Hero.inPit = True
        Kernel.instance.curTile().glyph = '^'
    def found_beartrap(self):
        Kernel.instance.log("Found a beartrap. Setting tile to ^")
        Kernel.instance.curTile().glyph = '^'
    def stepped_in_beartrap(self):
        Kernel.instance.log("Just stepped into a beartrap :(")
        Kernel.instance.Hero.inBearTrap = True
        Kernel.instance.curTile().glyph = '^'
    def trigger_trap(self):
        #TODO
        Kernel.instance.log("Triggered a trap, setting glyph to ^.. Not changing color yet")
        Kernel.instance.curTile().glyph = '^'

    def blinded(self):
        Kernel.instance.log("I got blinded.")
        Kernel.instance.Hero.blind = True

    def gain_instrinct(self, type):
        pass
    def skill_up(self, match):
        if match.groups()[0] == 'weapon':
            Kernel.instance.log("Enhanced weaponskill!")
            pass

    def open_door_here(self):
        Kernel.instance.log("Setting tile to '-' with door colors")
        Kernel.instance.curTile().glyph = '-'
        Kernel.instance.curTile().color = TermColor(33, 0, False, False)

    def call_potion(self, match):
        Kernel.instance.send("\x1b")
        Kernel.instance.dontUpdate()

    def eat_it(self):
        Kernel.instance.log('eating...')
        Kernel.instance.send('y')
        Kernel.instance.dontUpdate()

    def no_door(self):
        Kernel.instance.Hero.lastActionedTile.is_door = False

    def eat(self, matched):
        options = matched.groups()[0]
        Kernel.instance.log('eating...' + options)
        if 'f' in options:
            Kernel.instance.send('f')
        else:
            Kernel.instance.send(options[0])
        Kernel.instance.dontUpdate()

    def is_weak(self):
        Kernel.instance.sendSignal("s_isWeak")

    def is_staircase_here(self, match):
        Kernel.instance.log("Found staircase under some items..")

        if match.groups()[0] == 'down':
            Kernel.instance.curTile().glyph = '>'
            Kernel.instance.curTile().color = TermColor(37, 0, False, False)
        else:
            Kernel.instance.curTile().glyph = '<'
            Kernel.instance.curTile().color = TermColor(37, 0, False, False)

    def leg_no_shape(self):
        Kernel.instance.log("Leg is not in shape :'(")
        Kernel.instance.Hero.legShape = False

    def leg_feels_better(self):
        Kernel.instance.log("Leg is fine again.")
        Kernel.instance.Hero.legShape = True

    def found_items(self, tmp):
        Kernel.instance.log("Found some item(s)..")
        Kernel.instance.sendSignal("foundItemOnFloor")
        if Kernel.instance.Dungeon.curBranch:
            Kernel.instance.log("Updating items on (%s)" % Kernel.instance.curTile())
            for item in Kernel.instance.curTile().items:
                item.appearance = "Dummy"

    def shop_entrance(self):
        Kernel.instance.log("Found a shop.")
        buf = [Kernel.instance.curTile()]
        while buf:
            for tile in buf.pop().neighbours():
                # This could break once a year or so (if a monster is standing in a non-shop square after you login?)
                if (tile.glyph == '.' or tile.monster or tile.items) and not tile.inShop:
                    buf.append(tile)

                    Kernel.instance.log("Setting %s to be inside a shop." % tile)
                    tile.inShop = True


    def graffiti_on_floor(self):
        Kernel.instance.log("Found grafitti!")

    def parseMessages(self):
        if not self.updateNext:
            self.updateNext = True
            return

        for msg in self.messages:
            for event in self.events:
                match = re.search(event, msg)
                if match:
                    Kernel.instance.log("Found message: %s" % event)
                    for member in inspect.getmembers(self):
                        if member[0] == self.events[event][0]:
                            Kernel.instance.log("Calling method (%s)" % event)
                            func = member[1]
                            if len(inspect.getargspec(func)[0]) > 1:
                                func(match)
                            else:
                                func()

        self.messages = []

    def dontUpdate(self):
        Kernel.instance.log("Someone told the Senses not to update this tick! Probably myself")
        self.updateNext = False

from nethack_raph.myconstants import TTY_HEIGHT, DUNGEON_WIDTH

import inspect
import re


class Senses:
    def __init__(self, kernel):
        self.kernel = kernel
        self._state = 'default'
        self.rx_paginated = re.compile(
            r"""^[^\(]*
            \(
                (?P<curr>\d+)
                \s of \s
                (?P<total>\d+)
            \)
            [^\)]*$
            """,
            re.VERBOSE | re.IGNORECASE | re.MULTILINE | re.ASCII,
        )
        self.rx_enh_option = re.compile(
        r"""^(?:
            (?P<letter>[a-z])\s-  # the option letter [OPTIONAL]
        )?\s+
            (?P<skill>[^\[\n]+?)    # the skill name
        \s+\[
            (?P<level>[^\]]+)     # the skill level
        \]\s*$
        """,
        re.VERBOSE | re.IGNORECASE | re.MULTILINE | re.ASCII,
    )
        self.messages = []

        self.events = {
            # "(needs food, badly!|feel weak now\.|feel weak\.)":              ['is_weak'],
            "You feel that .* is displeased.":                               ['is_displeased'],
            "There is a staircase (down|up) here":                           ['is_staircase_here'],
            "Your (right|left) leg is in no shape":                          ['leg_no_shape'],
            "Your leg feels somewhat better":                                ['leg_feels_better'],
            "You see here":                                                  ['found_items'],
            "There are (several|many) objects here":                         ['found_items'],
            "There's some graffiti on the floor here":                       ['graffiti_on_floor'],
            "You read: \"(.*?)\"":                                           ['you_read'],
            "Velkommen, [^,]+!":                                             ['shop_entrance'],
            ".*elcome to .* (" \
                "store|dealership|bookstore|emporium|" \
                "outlet|delicatessen|jewelers|accessories|hardware|" \
                "books|food|lighting" \
            ").*":                                                           ['shop_entrance'],
            "You can't move diagonally into an intact doorway.":             ['open_door_there'],
            "You can't move diagonally out of an intact doorway.":           ['open_door_here'],
            "There is an open door here":                                    ['open_door_here'],
            "There is a bear trap here|You are caught in a bear trap":       ['found_beartrap'],
            "You feel more confident in your ([^ ]+) ":                      ['skill_up'],
            "You feel you could be more dangerous!":                         ['skill_up'],
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
            "There is a teleportation trap here":                            ['found_trap', 'teleport'],

            # r".* eat it\? \[ynq\] \(n\)":                                    ['eat_it'],
            "You see no door there.":                                        ['no_door'],
            "You finish eating .*":                                          ['food_is_eaten'],
            "You harmlessly attack a statue.":                               ['is_statue'],
            "You cannot pass through the bars.":                             ['not_walkable'],
            "You are carrying too much to get through.":                     ['not_walkable'],
            "Hello stranger, who are you?":                                  ['who_are_you'],
            "It's solid stone.":                                             ['not_walkable'],
            "Will you please leave your (.*) outside\?":                     ['leave_pick'],
            "Call a scroll .*":                                              ['scroll'],
            "You don't have anything to eat.":                               ['no_food'],
            "You don't have anything else to wear.":                         ['no_wear'],
            "You don't have anything else to put on.":                       ['no_wear'],
            "Call a scroll labeled .*":                                      ['read_scroll'],
            "(.+) engulfs you":                                              ['got_engulfed'],
            "Call (.+) potion":                                              ['call_potion'],
            "You kill .*":                                                   ['killed_monster'],
            "Continue eating\? .*":                                          ['stop_eating'],
            "You see no objects here.":                                      ['nothing_found'],
            "You can't write on the .*":                                     ['cant_write'],
            "You are hit.*":                                                 ['you_were_hit'],
            "There is nothing here to pick up.":                             ['no_pickup'],
            "The stairs are solidly fixed to the floor.":                    ['no_pickup'],
            "You could drink the water...":                                  ['no_pickup'],
            "It won't come off the hinges.":                                 ['no_pickup'],
            "The plumbing connects it to the floor.":                        ['no_pickup'],
            "You cannot wear .*":                                            ['cant_wear'],
            "You are already wearing .*":                                    ['cant_wear'],
            "[a-zA-Z] - ":                                                   ['picked_up'],
            "You finish your dressing maneuver.":                            ['dressed'],
            "You finish taking off your mail.":                              ['took_off'],
            r".*rop .*(gold|money).*":                                       ['drop_gold'],
            "They are cursed.":                                              ['cursed_boots'],
        }

    def update(self):
        ker = self.kernel()

        # XXX this is where the top line is used, can we reuse the message?
        top = ker.top_line()
        self.messages = self.messages + top.strip().split("  ")

        #TODO MOVE THE ABOWE TO UPDATE

        if ker.searchTop("In what direction?"):
            # breakpoint()
            ker.log("Getting rid if 'In what direction?' prompt")
            ker.send("\x1b")

        match = ker.searchTop(r"What do you want to eat\? \[(.*) or \?\*\]")
        if match:
            self.what_to_eat(match)
            return

        elif ker.searchTop(r".* eat .*\? \[ynq\] \(n\)"):
            self.eat_it(message=ker.top_line())
            return

        elif ker.searchTop(r"What do you want to write in the dust here\?"):
            ker.send('Elbereth\r')
            ker.hero.read()
            return

        elif ker.searchTop(r"Do you want to add to the current engraving\? \[ynq\] \(y\)"):
            ker.send('n')
            return

        elif ker.searchTop("You have .* trouble lifting .* corpse .*"):
            ker.curLevel().clear_items(*ker.hero.coords())
            ker.send('n')
        elif ker.searchTop("You have much trouble lifting .*"):
            ker.curLevel().clear_items(*ker.hero.coords())
            ker.send('n')
            return
        elif ker.searchTop("You have a little trouble lifting .*"):
            ker.send('y')
            return

        elif ker.searchTop("Really attack the guard\? \[yn\] \(n\)"):
            ker.send('n')
            return
        elif ker.searchTop("Really attack"):
            ker.log("Asked if I really want to attack.")
            ker.send("y")
            return

        elif ker.searchTop("Eat it? [yn]"):  # opened tin prompt
            ker.send("y")
            return

        elif ker.searchTop("\? \[(.*?)\]"):
            ker.log("Found a prompt we can't handle: %s" % ker.top_line())
            ker.send(" ")

    def drop_gold(self, *, match=None, message=None):
        ker = self.kernel()
        ker.send('d$')
        ker.curTile().dropped_here = True

    def got_expelled(self, *, match=None, message=None):
        ker = self.kernel()
        ker.log("Got expelled. Phew!")
        ker.hero.isEngulfed = False

    def got_engulfed(self, *, match, message=None):
        ker = self.kernel()
        ker.log("We just got engulfed. This will confuze me a whole lot :(")
        ker.hero.isEngulfed = True

    def shopkeep_door(self, *, match=None, message=None):
        ker = self.kernel()

        neighbours = ker.curLevel().neighbours[ker.hero.coords()]
        neighbours.shopkeep_door[neighbours.is_closed_door] = True

    def locked_door(self, *, match=None, message=None):
        ker = self.kernel()
        if ker.hero.lastActionedTile is None:
            return

        tile = ker.curLevel().tiles[ker.hero.lastActionedTile]
        if tile.is_closed_door:
            tile.locked = True

    def found_trap(self, type, *, match=None, message=None):
        ker = self.kernel()
        ker.log("I found a trap. Setting char to ^")
        ker.curLevel().set_as_trap(ker.curTile())

    def fell_into_pit(self, *, match=None, message=None):
        ker = self.kernel()
        ker.log("I fell into a pit :(")
        ker.hero.inPit = True
        ker.curLevel().set_as_trap(ker.curTile())

    def found_beartrap(self, *, match=None, message=None):
        ker = self.kernel()
        ker.log("Found a beartrap. Setting tile to ^")
        ker.curLevel().set_as_trap(ker.curTile())

    def stepped_in_beartrap(self, *, match=None, message=None):
        ker = self.kernel()
        ker.log("Just stepped into a beartrap :(")
        ker.hero.inBearTrap = True
        ker.curLevel().set_as_trap(ker.curTile())

    def trigger_trap(self, *, match=None, message=None):
        ker = self.kernel()
        ker.log("Triggered a trap, setting char to ^.. Not changing color yet")
        ker.curLevel().set_as_trap(ker.curTile())

    def blinded(self, *, match=None, message=None):
        ker = self.kernel()
        ker.log("I got blinded.")
        ker.hero.blind = True

    def gain_instrinct(self, type, *, match=None, message=None):
        pass

    def skill_up(self, *, match, message=None):
        self.kernel().hero.can_enhance = True

    def open_door_here(self, *, match=None, message=None):
        ker = self.kernel()
        lev = ker.curLevel()

        tile = lev.tiles[ker.hero.coords()]
        if not tile.is_opened_door:
            lev.set_as_door(tile)

    def open_door_there(self, *, match=None, message=None):
        ker = self.kernel()
        lev = ker.curLevel()
        if ker.hero.lastActionedTile is None:
            return
        

        tile = lev.tiles[ker.hero.lastActionedTile]
        if not tile.is_opened_door:
            lev.set_as_door(tile)

    def call_potion(self, *, match, message=None):
        self.kernel().send("\x1b")

    def eat_it(self, *, match=None, message):
        ker = self.kernel()
        lev = ker.curLevel()
        x, y = ker.hero.coords()

        if ker.hero.lastAction == 'eat_from_inventory':
            ker.log('eating from inventory. eating aborted')
            ker.send('n')
            return

        if not all([it.is_food for it in lev.items[x, y] if it.char == '%' and not it.corpse]):
            # otherwise we should check that food in msg correspond to edible food
            ker.log('inedible: eating aborted')
            ker.send('n')
            for item in lev.items[x, y]:
                if item.char == '%':
                    item.is_food = False
            return

        corpses = [it.is_food and not it.is_tainted() for it in lev.items[x, y] if it.corpse]
        if 'corpse' in message and (not corpses or not all(corpses)):
            ker.log('unknown / inedible corpse: eating aborted')
            ker.send('n')
            for it in lev.items[x, y]:
                if it.char == '%':
                    it.is_food = False
            return

        if 'glob of' in message:
            ker.log('glob: eating aborted')
            ker.send('n')
            for it in lev.items[x, y]:
                if it.char == '%':
                    it.is_food = False
            return

        ker.log('eating...')
        ker.send('y')

    def no_door(self, *, match=None, message=None):
        ker = self.kernel()
        if ker.hero.lastActionedTile:
            tile = ker.curLevel().tiles[ker.hero.lastActionedTile]
            tile.is_closed_door = False

    def what_to_eat(self, matched):
        ker = self.kernel()
        options = matched.groups()[0]
        ker.log('eating...' + options)
        if 'f' in options:
            ker.send('f')
        else:
            ker.send(options[0])

    def is_displeased(self, *, match=None, message=None):
        ker = self.kernel()
        ker.hero.god_is_angry = True

    def is_staircase_here(self, *, match, message=None):
        ker = self.kernel()
        ker.log("Found staircase under some items..")

        if match.groups()[0] == 'down':
            ker.curTile().char = '>'
        else:
            ker.curTile().char = '<'

    def leg_no_shape(self, *, match=None, message=None):
        ker = self.kernel()

        #TODO DONT WORK
        ker.log("Leg is not in shape :'(")
        ker.hero.legShape = False

    def leg_feels_better(self, *, match=None, message=None):
        ker = self.kernel()

        ker.log("Leg is fine again.")
        ker.hero.legShape = True

    def found_items(self, *, match, message):
        ker = self.kernel()

        ker.log("Found some item(s)..")

    def shop_entrance(self, *, match, message):
        # acquire ref to the kernel
        ker = self.kernel()
        hero, lev = ker.hero, ker.curLevel()
        curr = lev.tiles[hero.coords()]

        ker.log("Found a shop.")
        if curr.is_opened_door and hero.lastAction == 'move':
            prev_coords = hero.beforeMove
            cur_coords = hero.coords()
            if max(abs(c - p) for c, p in zip(cur_coords, prev_coords)) == 1:

                # entrance is opposite to the tile where we came from
                entrance_x, entrance_y = tuple((2 * c - p) for c, p in zip(cur_coords, prev_coords))
                entrance_tile = lev.tiles[entrance_x, entrance_y]

                entrance_tile.shop_entrance = True
                lev.update_walk_cost(entrance_tile)
                ker.log(f'Shop entrance: {entrance_tile}')

        buf = [curr]
        while buf:
            for tile in lev.adjacent(buf.pop()):
                # This could break once a year or so (if a monster is standing in a non-shop square after you login?)
                x, y = tile.xy
                is_monster = (x, y) in lev.monsters and not lev.monsters[x, y].pet
                is_item = bool(lev.items[x, y])

                if (tile.char == '.' or is_monster or is_item) and not tile.in_shop:
                    buf.append(tile)
                    ker.log("Setting %s to be inside a shop." % tile)
                    lev.tiles[x, y].in_shop = True

    def food_is_eaten(self, *, match=None, message=None):
        ker = self.kernel()
        items = ker.curLevel().items[ker.hero.coords()]

        if ker.hero.lastAction == 'eat_from_inventory':
            return

        if 'corpse' in message:
            corpse_count = len([it for it in items if it.corpse])
            if corpse_count > 0:
                # delete eaten corpse
                idx = next((i for i, it in enumerate(items) if it.corpse), None)
                items.pop(idx)

            # mark all others as unedible
            for item in ker.curLevel().items[ker.hero.coords()]:
                if item.corpse:
                    item.is_food = False

            return

        if len([it for it in items if it.is_food]) > 0:
            # delete one is_food item
            idx = next((i for i, it in enumerate(items) if it.is_food), None)
            items.pop(idx)
            return

        # probably ate something wrong
        ker.log('not edible: eating aborted')
        ker.send('n')

    def no_food(self, *, match=None, message=None):
        ker = self.kernel()
        for item in ker.curLevel().items[ker.hero.coords()]:
            if item.char == '%':
                item.is_food = False

    def stop_eating(self, *, match=None, message):
        ker = self.kernel()

        # probably ate something wrong
        ker.log('not edible: eating aborted')
        ker.send('n')
        for item in ker.curLevel().items[ker.hero.coords()]:
            if item.char == '%':
                item.is_food = False

    def no_wear(self, *, match=None, message=None):
        self.kernel().inventory.new_armors = []

    def read_scroll(self, *, match=None, message=None):
        self.kernel().send('r\r') # 'r\r' seems to work

    def is_statue(self, *, match=None, message=None):
        ker = self.kernel()
        lev = ker.curLevel()

        last = ker.hero.lastActionedTile  # x-y coords
        if last is not None and last in lev.monsters:
            lev.monsters[last].is_statue = True

    def not_walkable(self, *, match=None, message=None):
        ker = self.kernel()
        lev = ker.curLevel()

        last = ker.hero.lastActionedTile  # x-y coords
        if last is not None:
            tile = lev.tiles[last]
            tile.walkable_glyph = False
            lev.update_walk_cost(tile)

    def leave_pick(self, *, match, message=None):
        pass

    def who_are_you(self, *, match=None, message=None):
        # XXX dubious strategy... failed for a vutpurse in a vault on level 1
        self.kernel().send('Croseus\r')

    def scroll(self, *, match=None, message=None):
        self.kernel().send('r')

    def carrying_too_much(self):
        ker = self.kernel()
        lev = ker.curLevel()

        # FIXME (dima) drop smth
        last = ker.hero.lastActionedTile  # x-y coords
        if last is not None:
            tile = lev.tiles[last]
            tile.walkable_glyph = False
            lev.update_walk_cost(tile)

    def graffiti_on_floor(self, *, match=None, message=None):
        self.kernel().log("Found grafitti!")

    def killed_monster(self, *, match, message):
        ker = self.kernel()
        lev = ker.curLevel()

        last = ker.hero.lastActionedTile  # x-y coords
        if last is None:
            return

        for it in lev.items[last]:
            if it.corpse and it.corpse in message and it.turn_of_death < 0:
                it.turn_of_death = ker.hero.turns

    def you_read(self, *, match, message=None):
        ker = self.kernel()

        ker.log(f'YOU READ {match.groups()[0]}')
        ker.curTile().has_elbereth = match.groups()[0] == 'Elbereth'

    def nothing_found(self, *, match=None, message=None):
        ker = self.kernel()
        ker.curLevel().clear_items(*ker.hero.coords())

    def cant_write(self, *, match=None, message=None):
        tile = self.kernel().curTile()
        if tile.char == '':
            tile.char = '{'

    def you_were_hit(self, *, match=None, message=None):
        ker = self.kernel()
        if ker.curTile().has_elbereth:
            # you was hit, possible from distance, elbereth doesn't protect you
            for mon in ker.curLevel().monsters.values():
                if not mon.pet:
                    mon.range_attack = True

    def no_pickup(self, *, match=None, message=None):
        ker = self.kernel()
        ker.curLevel().clear_items(*ker.hero.coords())

    def picked_up(self, *, match=None, message=None):
        ker = self.kernel()
        if ker.hero.lastAction != 'pick':
            return

        ker.curLevel().clear_items(*ker.hero.coords())

    def dressed(self, *, match=None, message=None):
        ker = self.kernel()
        if ker.hero.armor_class >= ker.hero.armor_class_before:
            ker.inventory.take_off_armors.append(ker.hero.lastActionedItem)

        if ker.hero.gain_levitation:  # consider levitation as a bad thing
            ker.inventory.take_off_armors.append(ker.hero.lastActionedItem)

    def took_off(self, *, match=None, message=None):
        ker = self.kernel()
        # Drop unused item:
        ker.log(f'Drop item {ker.hero.lastActionedItem}')
        ker.send(f'd{ker.hero.lastActionedItem}')
        ker.curTile().dropped_here = True

    def cursed_boots(self, *, match=None, message=None):
        ker = self.kernel()
        if ker.hero.levitating:
            ker.hero.levitating_curse = True

    def cant_wear(self, *, match=None, message=None):
        ker = self.kernel()
        # Drop unused item:
        ker.log(f'Drop item {ker.hero.lastActionedItem}')
        ker.send(f'd{ker.hero.lastActionedItem}')
        ker.curTile().dropped_here = True
        # TODO (nikita): we can try take off another item, if we are already wearing that type of armor

    def parse_messages(self):
        ker = self.kernel()
        members = dict(inspect.getmembers(self))

        for msg in self.messages:
            for event, (handler, *args) in self.events.items():
                match = re.search(event, msg)
                if not match:
                    continue

                ker.log("Found message: %s" % event)
                if handler in members:
                    ker.log("Calling method (%s)" % event)
                    members[handler](*args, match=match, message=msg)

        self.messages = []

    def parse_menu(self):
        ker = self.kernel()
        lev = ker.curLevel()
        x, y = ker.hero.coords()
        header = ker.get_row_line(0)
        skip_first = len(header) - len(header.lstrip())

        # What to pick up menu
        if header and header.find("Pick up what?") >= 0:

            rows = [ker.get_row_line(i)[skip_first:] for i in range(1, TTY_HEIGHT + 1)]
            choice = ker.hero.pick_up_choice(rows)

            ker.curLevel().clear_items(*ker.hero.coords())
            ker.log(f'Pick up what choice: {choice}')
            ker.send(''.join(choice) + '\r')

        elif header and header.find("attributes:") >= 0:  # parsing agent's attributes at the start
            msg = self.kernel().get_row_line(3) + self.kernel().get_row_line(4)
            self.kernel().hero.set_attributes(msg)
            self.kernel().send('  ')

        elif header and header.find("There is an open door here") >= 0:
            self.open_door_here()
            ker.send(' ')

        elif header and header.find("Things that are here:") >= 0:
            rows = [ker.get_row_line(i)[skip_first:] for i in range(1, TTY_HEIGHT + 1)]
            if sum(['corpse' in row for row in rows]) > 1:  # there are several corpse here. don't want to mix them up
                ker.log(f'corpse savety check {[row for row in rows[:8]]}')
                for it in lev.items[x, y]:
                    if it.is_food and it.corpse:
                        it.is_food = False
            ker.send(' ')
        elif header and header.find("Current skills") >= 0 or self._state == 'in_skills_menu':
            self._state = 'in_skills_menu'
            rows = [ker.get_row_line(i)[skip_first:] for i in range(1, TTY_HEIGHT + 1)]
            ker.hero.parse_current_skills(rows)

            screen = '\n'.join([ker.get_row_line(i).strip() for i in range(1, TTY_HEIGHT + 1)])
            match = self.rx_paginated.search(screen)
            is_last_page = True
            if match is not None:
                curr, total = map(int, match.groups())
                is_last_page = curr == total

            self._state = 'default' if is_last_page else 'in_skills_menu'
            ker.send(' ')

        elif header and header.find("Pick a skill to advance") >= 0 or self._state == 'in_enhance_menu':
            if self._state == 'in_enhance_menu':  # second page of the paginated menu
                skip_first = 0

            screen = '\n'.join([ker.get_row_line(i)[skip_first:].strip() for i in range(TTY_HEIGHT + 1)])
            self._state = 'in_enhance_menu'

            match = self.rx_paginated.search(screen)
            is_last_page = True
            if match is not None:
                curr, total = map(int, match.groups())
                is_last_page = curr == total

            for letter, skill, level in self.rx_enh_option.findall(screen):
                if letter:
                    ker.send(letter)
                    self._state = 'default'
                    ker.hero.can_enhance = False
                    ker.hero.skills[skill] += 1
                    ker.log(f'current skills: {ker.hero.skills}')
                    return

            if is_last_page:
                self._state = 'default'
                ker.hero.can_enhance = False
            ker.send(' ')

        else:
            ker.send(' ')

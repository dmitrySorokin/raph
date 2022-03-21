import re

from collections import defaultdict


class Hero:
    def __init__(self, kernel):
        self.kernel = kernel
        self.x = None
        self.y = None
        self.beforeMove = None
        self.tmpCount = 0
        self.turns = 0

        self.strength = None
        self.dexterity = None
        self.constitution = None
        self.intelligence = None
        self.wisdom = None
        self.charisma = None

        self.score = 0
        self.curhp = None
        self.maxhp = None
        self.gold = None
        self.curpw = None

        self.maxpw = None
        self.armor_class = None
        self.xp = None
        self.xp_next = None
        self.level_number = None
        self.encumbered_status = None  # Unencumbered / Burdened / Stressed / Strained / Overtaxed / Overloaded

        self.blind = False
        self.confused = False
        self.hallu = False
        self.stun = False
        self.levitating = False
        self.legShape = True
        self.gain_levitation = False
        self.levitating_curse = False

        self.inBearTrap = False
        self.inPit = False
        self.isEngulfed = False
        self.isLycanthropy = False
        self.foodPoisoned = False

        self.hunger = None
        self.god_is_angry = False

        self.role = None
        self.race = None
        self.gender = None
        self.moral = None

        self.lastActionedTile = None  # I sersiouly need to #enhance my english skills :'(
        self.lastAction = None
        self.lastActionedItem = None

        self.armor_class_before = None

        self.pick_up_weapon = True
        self.pick_up_armor = True
        self.pick_up_projectives = True
        self.use_range_attack = True
        self.use_launchers = False
        self.prefer_melee_attack = True

        self.spells = {}
        self.skills = defaultdict(int)
        self.can_enhance = False

    def coords(self):
        return self.x, self.y

    def update(self, blstats, top_line, bot_line):
        # TODO: use them
        # strength_percentage, monster_level, dungeon_number, level_number, condition
        # condition (aka `unk`) == 64 -> Deaf

        levitating = bool(re.search("Lev", bot_line))
        self.gain_levitation = not self.levitating and levitating
        if self.levitating and not levitating:
            self.levitating_curse = False
        self.levitating = levitating

        self.blind = bool(re.search("Blind", bot_line))
        self.confused = bool(re.search("Conf", bot_line))
        self.stun = bool(re.search("Stun", bot_line))
        self.hallu = bool(re.search("Hallu", bot_line))
        self.foodPoisoned = bool(re.search("FoodPois", bot_line))

        self.y, self.x, strength_percentage, self.strength, self.dexterity, self.constitution, \
            self.intelligence, self.wisdom, self.charisma, self.score, self.curhp, self.maxhp, \
            _, self.gold, self.curpw, self.maxpw, self.armor_class, monster_level, \
            self.xp, self.xp_next, self.turns, self.hunger, self.encumbered_status, dungeon_number, \
            self.level_number, condition = blstats

        self.kernel().log(f'Hero hp: {self.curhp}/{self.maxhp}, hero coords: {self.coords()}')

    def attack(self, tile):
        dir = self._get_direction(self.coords(), tile)
        self.kernel().drawString("Attacking -> %s (%s)" % (dir, tile))
        self.kernel().send("F"+dir)
        self.lastActionedTile = tile
        self.lastAction = 'attack'

    def throw(self, tile, weapon_letter):
        dir = self._get_direction(self.coords(), tile)
        self.kernel().drawString(f"Range attacking (throw) -> {dir} ({tile}) {weapon_letter}")
        self.kernel().send("t" + weapon_letter + dir)
        self.lastActionedTile = tile
        self.lastAction = 'throw'

    def launch(self, tile, launcher, missle):
        dir = self._get_direction(self.coords(), tile)
        self.kernel().drawString(f"Range attacking (launch) -> {dir} ({tile} {launcher} {missle})")
        wielded = self.kernel().inventory.wielded()

        if wielded != launcher:
            self.kernel().send("w" + launcher + ' ')  # wield launcher
        self.kernel().send("t" + missle + dir)  # fire from launcher
        if self.prefer_melee_attack and wielded != launcher:
            self.kernel().inventory.new_weapons.append(wielded)   # wield back

        self.kernel().log(f'{self.kernel().action}')

        self.lastActionedTile = tile
        self.lastAction = 'launch'

    def cast_dir_spell(self, tile, spell_letter):
        dir = self._get_direction(self.coords(), tile)
        self.kernel().drawString(f"Casting -> {dir} ({tile}) ({spell_letter})")
        self.kernel().send("Z" + spell_letter + dir)

    def cast_spell(self, spell_letter):
        self.kernel().drawString(f"Casting {spell_letter}")
        self.kernel().send("Z" + spell_letter + '.')

    def use_dir_item(self, tile, letter):
        dir = self._get_direction(self.coords(), tile)
        self.kernel().drawString(f"Using item -> {dir} ({tile}) {letter}")
        self.kernel().send("a" + letter + dir)

    def move(self, tile):
        dir = self._get_direction(self.coords(), tile)
        self.kernel().drawString("Walking -> %s (%s)" % (dir, tile))

        self.beforeMove = (self.x, self.y)
        self.kernel().send(dir)
        self.lastActionedTile = tile
        self.lastAction = 'move'

    def descend(self):
        self.kernel().drawString(f"Hero (level: {self.xp}) is descending from level {self.level_number}")
        self.kernel().send(">")
        self.lastAction = 'descend'

    def open(self, tile):
        dir = self._get_direction(self.coords(), tile)
        self.kernel().log("Hero is opening a door..")
        self.kernel().send("o%s" % dir)
        self.lastActionedTile = tile
        self.lastAction = 'open'

    def kick(self, tile):
        dir = self._get_direction(self.coords(), tile)
        self.kernel().log("Hero is kicking a door..")
        self.kernel().send("\x04%s" % dir)
        self.lastAction = 'kick'

    def search(self, times=1):
        self.kernel().send("%ds" % times)

        neighbours = self.kernel().curLevel().neighbours[self.kernel().hero.coords()]
        neighbours.searches += times
        neighbours.searched[neighbours.searches >= self.kernel().curLevel().maxSearches] = True

        self.lastAction = 'search'

    def eat(self):
        self.kernel().log("Hero::eat")
        self.kernel().send("e")
        self.lastAction = 'eat'

    def eat_from_inventory(self):
        self.kernel().log("Hero::eat from inventory")
        self.kernel().send("e")
        self.lastAction = 'eat_from_inventory'

    def read(self):
        self.kernel().log("Hero::read")
        self.kernel().send(":")
        self.kernel().curTile().has_elbereth = False
        self.lastAction = 'read'

    def write(self):
        self.kernel().log("Hero::write in the dust")
        self.kernel().send('E-')
        self.lastAction = 'write'

    def engrave(self):
        self.kernel().log("Hero::engrave")
        self.kernel().send('E')
        self.lastAction = 'engrave'

    def pray(self):
        self.kernel().log("Hero::pray")
        self.kernel().send('#pray\ry')
        self.lastAction = 'pray'

    def pick(self):
        self.kernel().log("Hero::pick")
        self.kernel().send(',')
        self.lastAction = 'pick'

    def wear(self, armor_letter):
        self.kernel().log("Hero::wear")
        self.kernel().send(f'W*{armor_letter}')
        self.armor_class_before = self.armor_class
        self.lastAction = 'wear'
        self.lastActionedItem = armor_letter

    def take_off(self, armor_letter):
        self.kernel().log("Hero::take_off")
        if self.kernel().inventory.being_worn_count > 1:
            # have to define, what we want to take off
            self.kernel().send(f'T*{armor_letter}')
        else:
            self.kernel().send('T')
        self.lastAction = 'take_off'
        self.kernel().hero.lastActionedItem = armor_letter

    def wield(self, weapon_letter):
        self.kernel().log("Hero::wield")
        self.kernel().send(f'w*{weapon_letter}')
        self.lastAction = 'wield'

    def quiver(self, weapon_letter):
        self.kernel().log("Hero::quiver")
        self.kernel().send(f'Q*{weapon_letter}')
        self.lastAction = 'quiver'

    def drop_item(self, item_letter):
        self.kernel().log("Hero::drop item")
        self.kernel().send(f'd{item_letter}')
        self.kernel().curTile().dropped_here = True
        self.lastAction = 'drop_item'

    def quaff(self, potion_letter):
        self.kernel().log("Hero::quaff")
        self.kernel().send(f'q{potion_letter}')
        self.lastAction = 'quaff'

    def enhance(self):
        """Advance or check weapons skills."""
        self.kernel().send('#enh\r')

    def _get_direction(self, source, target):
        source_x, source_y = source
        target_x, target_y = target

        if abs(source_y - target_y) > 1 or abs(source_x - target_x) > 1:
            self.kernel().die(f"\n\nAsked for directions to a nonadjacent tile {source} -> {target}\n\n")

        if source_x < target_x and source_y < target_y:
            return 'n'
        if source_x < target_x and source_y == target_y:
            return 'j'
        if source_x < target_x and source_y > target_y:
            return 'b'
        if source_x == target_x and source_y < target_y:
            return 'l'
        if source_x == target_x and source_y > target_y:
            return 'h'
        if source_x > target_x and source_y < target_y:
            return 'u'
        if source_x > target_x and source_y == target_y:
            return 'k'
        if source_x > target_x and source_y > target_y:
            return 'y'

    def set_attributes(self, msg):
        if 'Archeologist' in msg:
            self.role = 'arc'
        elif 'Barbarian' in msg:
            self.role = 'bar'
        elif 'Caveman' in msg or 'Cavewoman' in msg:
            self.role = 'cav'
        elif 'Healer' in msg:
            self.role = 'hea'
        elif 'Knight' in msg:
            self.role = 'kni'
        elif 'Monk' in msg:
            self.role = 'mon'
        elif 'Priest' in msg or 'Priestest' in msg:
            self.role = 'pri'
        elif 'Ranger' in msg:
            self.role = 'ran'
        elif 'Rogue' in msg:
            self.role = 'rog'
        elif 'Samurai' in msg:
            self.role = 'sam'
        elif 'Tourist' in msg:
            self.role = 'tou'
        elif 'Valkyrie' in msg:
            self.role = 'val'
        elif 'Wizard' in msg:
            self.role = 'wiz'
        # else:
        #     raise Exception(f"Unknown role from '{msg}'")

        if 'human' in msg:
            self.race = 'hum'
        elif 'elf' in msg or 'elven' in msg:
            self.race = 'elf'
        elif 'dwar' in msg:
            self.race = 'dwa'
        elif 'gnom' in msg:
            self.race = 'gno'
        elif 'orc' in msg:
            self.race = 'orc'
        # else:
        #     raise Exception(f"Unknown race from '{msg}'")

        if 'female' in msg or 'woman' in msg or 'Priestess' in msg or 'dwarven' in msg:
            self.gender = 'fem'
        elif 'male' in msg or 'man' in msg or 'Priest' in msg or 'dwarf' in msg:
            self.gender = 'mal'
        # else:
        #     raise Exception(f"Unknown gender from '{msg}'")

        if 'neutral' in msg:
            self.moral = 'neu'
        elif 'lawful' in msg:
            self.moral = 'law'
        elif 'chaotic' in msg:
            self.moral = 'cha'
        # else:
        #     raise Exception(f"Unknown moral from '{msg}'")

        self.kernel().log(f"Hero is {self.role}-{self.race}-{self.moral}-{self.gender}")

        if self.role in {'ran', 'tou', 'wiz'}:
            self.prefer_melee_attack = False

        if self.role == 'wiz':
            self.spells['force_bolt'] = 'a'

        if self.role == 'hea':
            self.spells['healing'] = 'a'

        if self.role in {'ran'}:
            self.use_launchers = True

    def pick_up_choice(self, rows):
        # choose all armors to inventory
        projectives = [" spear", " dagger", " dart", " shuriken", " throwing star",
                       " knife", " stiletto", " scalpel", " crysknife"]

        stones = ['rock', 'stone']

        choice = []
        current_type = None
        for row in rows:
            if 'Weapon' in row:
                current_type = 'weapon'
                continue
            elif 'Armor' in row:
                current_type = 'armor'
                continue
            elif 'Gems/Stones' in row:
                current_type = 'stones'

            if self.pick_up_weapon and current_type == 'weapon':
                if row[0].islower():
                    choice.append(row[0])
                else:
                    current_type = None

            elif self.pick_up_armor and current_type == 'armor':
                if row[0].islower():
                    choice.append(row[0])
                else:
                    current_type = None

            elif self.pick_up_projectives and any(x in row for x in projectives):
                choice.append(row[0])

            elif self.use_launchers and current_type == 'stones' and any(x in row for x in stones):
                if row[0].islower():
                    choice.append(row[0])
                else:
                    current_type = None

            if 'gold piece' in row:
                choice.append('$')

        return choice

    def parse_current_skills(self, rows):
        skill_levels = ["Unskilled", "Basic",  "Skilled", "Expert", "Master", "Grand Master"]
        for row in rows:
            start = row.find('[')
            if start > 0:
                end = row.find(']')
                skill_level = row[start+1: end]
                skill = row[:start].strip()

                if skill_level in skill_levels and skill_levels.index(skill_level) > 0:
                    self.skills[skill] = skill_levels.index(skill_level)

        self.kernel().log(f'current skills: {self.skills}')

from nethack_raph.myconstants import OBJECT_CLASSES as OCLASSES
from nethack_raph.glossaries import WEAPON_GLOSSARY, ITEMS_TO_THROW, MELEE_WEAPON, LAUNCHERS, MISSILES

import numpy as np
import re

from functools import reduce
from operator import iadd


class Inventory:
    def __init__(self, kernel):
        self.kernel = kernel
        self.raw_glyphs = np.array((), dtype=np.int16)
        self.inv_strs = None
        self.inv_letters = None
        self.inv_oclasses = np.array((), dtype=np.int16)
        self.inv_glyphs = np.array((), dtype=np.int16)
        self.new_weapons = []
        self.new_armors = []
        self.take_off_armors = []
        self.items_to_drop = []
        self.healing_potions = []
        self.being_worn_count = None
        self.camera = None
        self.camera_charges = 0
        self.camera_letter = None
        self.launchers = {}

        self.skill_bonus = {
            0: -2,  # unskilled
            1: 0,   # basic
            2: 1,   # skilled
            3: 2    # expert
        }
        self.bare_hand_damage = {  # from https://nethackwiki.com/wiki/Bare_hands
            0: 1.5, 1: 2, 2: 2, 3: 2.5, 4: 3.5, 5: 3
        }
        self.martial_art_damage = {
            0: 3.25, 1: 4.75, 2: 5.5, 3: 7, 4: 7.75, 5: 9.25
        }

    def update(self, obs):
        self.raw_glyphs = np.copy(obs['inv_glyphs'])

        # parse the inventory
        inv_letters = obs['inv_letters'].view('c')  # uint8 to bytes
        index, = inv_letters.nonzero()  # keep non-empty slots only
        inv_strs = obs['inv_strs'].view('S80')[:, 0][index].astype(str)  # uint8 to sz
        inv_letters = inv_letters[index].astype(str)
        inv_oclasses = obs['inv_oclasses'][index]
        inv_glyphs = obs['inv_glyphs'][index]

        to_update = set()
        for i_class in ['WEAPON_CLASS', 'ARMOR_CLASS', 'POTION_CLASS', 'TOOL_CLASS', 'FOOD_CLASS', 'GEM_CLASS']:
            if (self.inv_oclasses == OCLASSES[i_class]).sum() < (inv_oclasses == OCLASSES[i_class]).sum():
                to_update.add(i_class)

        self.being_worn_count = len([oc for oc, inv_str in zip(inv_oclasses, inv_strs)
                                     if oc == OCLASSES['ARMOR_CLASS'] and 'being worn' in inv_str])

        self.inv_strs = inv_strs
        self.inv_letters = inv_letters
        self.inv_oclasses = inv_oclasses
        self.inv_glyphs = inv_glyphs

        # weapons
        if 'WEAPON_CLASS' in to_update:
            launchers = np.isin(self.inv_glyphs, LAUNCHERS)
            launch_skills = [WEAPON_GLOSSARY[g]['skill'] for g in self.inv_glyphs[launchers].tolist()]
            self.launchers = {}
            if launchers.sum() > 0:
                for glyph, inv_str, letter in zip(inv_glyphs[launchers], inv_strs[launchers], inv_letters[launchers]):
                    skill = WEAPON_GLOSSARY[glyph]['skill']
                    current_letter,  current_attack = self.launchers.get(skill, ('', -np.inf))
                    attack = self.weapon_exp_attack(glyph, inv_str)
                    if attack > current_attack:
                        self.launchers[skill] = letter, attack

            for oc, glyph, inv_str, letter in zip(inv_oclasses, inv_glyphs, inv_strs, inv_letters):
                if oc == OCLASSES['WEAPON_CLASS'] and 'weapon in hand' not in inv_str:
                    if glyph in ITEMS_TO_THROW:
                        continue
                    elif glyph in MELEE_WEAPON:
                        current_attack = self.current_exp_melee_attack()
                        if self.weapon_exp_attack(glyph, inv_str) > current_attack + 1:
                            self.new_weapons.append(letter)
                        else:
                            self.items_to_drop.append(letter)

                    elif glyph in LAUNCHERS:
                        skill = WEAPON_GLOSSARY[glyph]['skill']
                        if skill in self.launchers and self.launchers[skill][0] != letter:
                            self.items_to_drop.append(letter)

                    elif glyph in MISSILES:
                        if WEAPON_GLOSSARY[glyph]['skill'] not in launch_skills:
                            self.items_to_drop.append(letter)
                    else:
                        self.items_to_drop.append(letter)

        # gems
        if 'GEM_CLASS' in to_update:
            for oc, glyph, inv_str, letter in zip(inv_oclasses, inv_glyphs, inv_strs, inv_letters):
                if oc == OCLASSES['GEM_CLASS']:
                    if glyph in MISSILES:  # gray stone / rocks
                        if np.isin(self.inv_glyphs, 1975).sum() == 0:  # we don't have a sling to launch that missile
                            self.items_to_drop.append(letter)
                    else:
                        self.items_to_drop.append(letter)

        # armors
        if 'ARMOR_CLASS' in to_update:
            for oc, glyph, inv_str, letter in zip(inv_oclasses, inv_glyphs, inv_strs, inv_letters):
                if oc == OCLASSES['ARMOR_CLASS'] and 'being worn' not in inv_str:
                    self.new_armors.append((glyph, inv_str, letter))

        # potions
        if 'POTION_CLASS' in to_update:
            query = 'healing'
            potion_mask = inv_oclasses == OCLASSES['POTION_CLASS']
            if potion_mask.any():
                query_mask = np.char.find(inv_strs[potion_mask], query) >= 0
                self.healing_potions = inv_letters[potion_mask][query_mask].tolist()
            else:
                self.healing_potions = []

        # tools
        if 'TOOL_CLASS' in to_update:
            query = 'camera'
            query_mask = np.char.find(inv_strs, query) >= 0

            if query_mask.any():
                camera_str = inv_strs[query_mask][0]
                self.kernel().log(f'camera is available: {camera_str}')
                import re
                charges = re.search('.+camera \([0-9]+:([0-9]+)\)', camera_str)
                if charges:
                    self.camera_charges = int(charges.group(1))
                    self.kernel().log(f'camera has {self.camera_charges} charges')
                else:
                    self.kernel().log(f'parsing error: {camera_str}')
                self.camera_letter = inv_letters[query_mask].tolist()[0]
            else:
                self.kernel().log(f'camera is not found')
                self.camera_charges = 0

        # food
        if 'FOOD_CLASS' in to_update:
            food_mask = inv_oclasses == OCLASSES['FOOD_CLASS']
            if food_mask.any():
                query_mask = np.char.find(inv_strs[food_mask], 'corpse') >= 0
                # drop accidentally picked up corpse
                self.items_to_drop.extend(inv_letters[food_mask][query_mask].tolist())

    def have_food(self):
        food_mask = self.inv_oclasses == OCLASSES['FOOD_CLASS']
        return bool([x for x in self.inv_letters[food_mask] if x not in self.items_to_drop])

    def item_to_throw(self):
        range_weapons = [(l, g, s) for l, g, s in zip(self.inv_letters, self.inv_glyphs, self.inv_strs) \
                         if g in ITEMS_TO_THROW and 'weapon in hand' not in s]
        if range_weapons:
            range_weapon_letter, exp_damage = max(
                [(l, self.weapon_exp_attack(g, s)) for l, g, s in range_weapons],
                key=lambda x: x[1]
            )
            return range_weapon_letter, exp_damage

        else:
            return None, None

    def launcher_missile_pair(self):
        launchers = np.isin(self.inv_glyphs, LAUNCHERS)
        if launchers.sum() == 0:
            return None, None, None

        missiles = np.isin(self.inv_glyphs, MISSILES)
        missiles = zip(self.inv_letters[missiles], self.inv_glyphs[missiles], self.inv_strs[missiles])
        missiles = [(l, g, s) for l, g, s in missiles if WEAPON_GLOSSARY[g]['skill'] in self.launchers.keys()]

        if not missiles:
            return None, None, None

        missile_letter, glyph, exp_damage = max(
            [(l, g, self.weapon_exp_attack(g, s)) for l, g, s in missiles],
            key=lambda x: x[2]
        )
        launcher_letter = self.launchers[WEAPON_GLOSSARY[glyph]['skill']][0]
        return launcher_letter, missile_letter, exp_damage

    def current_exp_melee_attack(self):
        hero = self.kernel().hero
        wielded = (np.char.find(self.inv_strs, 'weapon in hand') > 0).nonzero()[0]
        if wielded.size > 0:
            ind = wielded[0]
            attack = self.weapon_exp_attack(self.inv_glyphs[ind], self.inv_strs[ind])

        elif hero.role in {'mon', 'sam'}:  # martial arts
            skill = hero.skills['martial arts']
            attack = self.martial_art_damage[skill]

        else:  # bare-handed
            skill = hero.skills['bare hands']
            attack = self.bare_hand_damage[skill]

        return attack

    def weapon_exp_attack(self, glyph, string):
        weapon = WEAPON_GLOSSARY.get(
            glyph,
            {'damage_S': '0', 'skill': '_'}  # for case when wielded not a weapon
        )

        damage_str = weapon['damage_S']
        damage = self.parse_damage_str(damage_str)

        # skill bonus
        skill = self.kernel().hero.skills[weapon['skill']]
        damage += self.skill_bonus[skill]

        # example '+2 knife'
        match = re.search('\+(\d+)', string)
        if match:
            damage += int(match.groups()[0])

        return damage

    def parse_damage_str(self, damage_str):
        """
        parsing damage string to expectation of damage
        :param damage_str:
        :return: expectation of damage

        Example:
        >>> self.parse_damage_str('2d3+1')
        5
        """

        damage_str = damage_str.split('+')
        if len(damage_str) > 1:
            return reduce(iadd, [self.parse_damage_str(x) for x in damage_str])
        else:
            damage_str = damage_str[0]

        d_pos = damage_str.find('d')
        if d_pos >= 0:
            res = (int(damage_str[d_pos + 1:]) + 1) / 2.
            if d_pos > 0:
                res *= int(damage_str[:d_pos])
            return res
        else:
            return int(damage_str)

    def wielded(self):
        wielded = (np.char.find(self.inv_strs, 'weapon in hand') > 0).nonzero()[0]
        if wielded.size > 0:
            ind = wielded[0]
            return self.inv_letters[ind]

        else:
            return '-'

import numpy as np

from nethack_raph.Actions.base import BaseAction
from nethack_raph.myconstants import COLOR_BG_YELLOW


class PickUpStuff(BaseAction):
    action_to_do = None

    def can(self, level):
        if self.kernel().inventory.take_off_armors:
            self.action_to_do = 'take_off'
            return True, np.ones(level.shape, dtype=bool)

        if self.kernel().inventory.new_armors:
            self.action_to_do = 'wear'
            return True, np.ones(level.shape, dtype=bool)

        if self.kernel().inventory.items_to_drop:
            self.action_to_do = 'drop_item'
            return True, np.ones(level.shape, dtype=bool)

        if self.kernel().inventory.new_weapons:
            self.action_to_do = 'wield'
            return True, np.ones(level.shape, dtype=bool)

        if self.hero.levitating:  # You cannot reach the floor.
            return False, np.zeros(level.shape, dtype=bool)

        if self.hero.encumbered_status >= 1:  # hero is burdened at least
            return False, np.zeros(level.shape, dtype=bool)

        stuff_tiles = np.zeros(level.shape, dtype=bool)
        for xy, items in level.items.items():
            if level.tiles[xy].in_shop or level.tiles[xy].dropped_here:
                continue

            # if xy in level.monsters:
            #     continue

            stuff = []
            for it in items:
                if it.item_type == 'gold_piece':
                    stuff.append(it)

                elif self.hero.pick_up_weapon and it.item_type == 'weapon':
                    stuff.append(it)

                elif self.hero.pick_up_armor and it.item_type == 'armor':
                    stuff.append(it)

                elif self.hero.pick_up_projectives and it.item_type == 'projective':
                    stuff.append(it)

                elif self.hero.use_launchers and it.item_type in {'launcher', 'missile'}:
                    stuff.append(it)

            if stuff:
                stuff_tiles[xy] = True
                self.action_to_do = 'pick_up'
                self.log(f"Found stuff {xy}: {list(map(str, stuff))}")

        return stuff_tiles.any(), stuff_tiles

    def execute(self, path):
        if self.action_to_do == 'wear':
            _, _, armor_letter = self.kernel().inventory.new_armors.pop(0)
            self.hero.wear(armor_letter)
            return

        if self.action_to_do == 'wield':
            weapon_letter = self.kernel().inventory.new_weapons.pop(0)
            self.hero.wield(weapon_letter)
            return

        if self.action_to_do == 'take_off':
            armor_letter = self.kernel().inventory.take_off_armors.pop(0)
            self.hero.take_off(armor_letter)
            return

        if self.action_to_do == 'drop_item':
            weapon_letter = self.kernel().inventory.items_to_drop.pop(0)
            self.hero.drop_item(weapon_letter)
            return

        # fetch an item
        *tail, one = path
        hero = self.hero
        assert one == (hero.x, hero.y)

        # move closer
        if tail:
            self.draw_path(path, color=COLOR_BG_YELLOW)
            hero.move(tail[-1])
            return

        hero.pick()

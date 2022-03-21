import numpy as np

from nethack_raph.Actions.base import BaseAction
from nethack_raph.myconstants import COLOR_BG_YELLOW


class EatFromInventory(BaseAction):
    def can(self, level):
        # XXX use meaningful constant name rather than a number here
        if self.hero.hunger >= 3:
            flag = self.kernel().inventory.have_food()
            self.log(f"Hero has food: {flag}")
            if flag:
                return True, None

        elif self.hero.hunger < 3:
            self.log(f"Hero is not weak")

        return False, None

    def execute(self, path=None):
        self.hero.eat_from_inventory()


class Eat(BaseAction):
    def can(self, level):
        if self.hero.hunger == 0:
            return False, np.zeros(level.shape, dtype=bool)

        if self.hero.levitating:  # cant eat while levitating
            return False, np.zeros(level.shape, dtype=bool)

        bad_monsters = [
            m for m in level.monsters.values()
            if m.is_attackable
        ]
        if bad_monsters:
            return False, np.zeros(level.shape, dtype=bool)

        consumable = np.zeros(level.shape, dtype=bool)
        for xy, items in level.items.items():
            if level.tiles[xy].char == '^' or level.tiles[xy].in_shop:
                continue

            food = [it for it in items if it.is_food and not it.is_tainted()]
            if food:
                self.log(f"Found food {xy}: {list(map(str, food))}")
                consumable[xy] = True

        return consumable.any(), consumable

    def execute(self, path):
        *tail, one = path
        assert one == (self.hero.x, self.hero.y)
        if tail:
            self.draw_path(path, color=COLOR_BG_YELLOW)
            self.hero.move(tail[-1])
            return

        self.hero.eat()

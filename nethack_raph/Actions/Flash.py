import numpy as np

from nethack_raph.Actions.base import BaseAction
from nethack_raph.Actions.ThrowAttack import range_attack_candidates


class Flash(BaseAction):
    def __init__(self, kernel):
        self.attack_direction = None
        self.selected_monster = None
        self.flashed_monster = None
        super().__init__(kernel)

    def can(self, level):
        if self.hero.curhp >= self.hero.maxhp *.5 and self.hero.xp > 1:
            return False, None

        if self.kernel().inventory.camera_charges < 1:
            return False, None

        monsters = range_attack_candidates(self.hero, level)

        not_flashed = [
            (m, dir, dist) for m, dir, dist in monsters
            if m.glyph != self.flashed_monster]

        if not_flashed:
            m, self.attack_direction, _ = min(not_flashed, key=lambda x: x[2])  # attack the closest monster
            self.selected_monster = m.glyph
            return True, None
        else:
            return False, None

    def execute(self, path=None):
        self.flashed_monster = self.selected_monster
        self.kernel().inventory.camera_charges -= 1
        self.hero.use_dir_item(self.attack_direction, self.kernel().inventory.camera_letter)

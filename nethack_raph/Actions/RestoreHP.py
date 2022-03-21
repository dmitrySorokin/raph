import numpy as np

from nethack_raph.Actions.base import BaseAction


class RestoreHP(BaseAction):
    def can(self, level):
        if self.hero.curhp >= self.hero.maxhp * .5: # hp is at an acceptable level
            return False, None

        # monsters nearby
        neighbours = level.neighbours[self.hero.x, self.hero.y].xy.flat
        bad_monsters = [
            level.monsters[xy] for xy in map(tuple, neighbours)
            if xy in level.monsters and level.monsters[xy].is_attackable
        ]
        if bad_monsters:
            return False, None

        # monsters with range attack
        bad_monsters = [
            m for m in level.monsters.values()
            if m.is_attackable and m.range_attack
        ]
        if bad_monsters:
            return False, None

        return True, None

    def execute(self, path=None):
        assert path is None

        self.log("Searching for 10 turns because my HP is low")
        self.hero.search(10)

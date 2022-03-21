import numpy as np

from nethack_raph.Actions.base import BaseAction
from nethack_raph.myconstants import COLOR_BG_RED


class FollowGuard(BaseAction):
    def can(self, level):
        targets = np.zeros(level.shape, dtype=bool)
        for xy, m in level.monsters.items():
            if m.guard:
                targets[xy] = True

        return targets.any(), targets

    def execute(self, path):
        guard, *middle, one = path
        if middle:
            self.log("Going towards guard")
            self.draw_path(path, color=COLOR_BG_RED)
            self.hero.move(middle[-1])
            return

        self.kernel().send(' ')

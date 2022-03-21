import numpy as np

from nethack_raph.Actions.base import BaseAction
from nethack_raph.myconstants import COLOR_BG_BLUE


class Explore(BaseAction):
    def can(self, level):
        assert self.kernel().curLevel() is level

        if level.explored:
            self.log("Level is explored.")
            return False, np.zeros(level.shape, dtype=bool)

        targets = level.tiles.walkable_tile & \
            ~level.tiles.explored & \
            ~level.tiles.is_hero & \
            ~level.tiles.in_shop

        self.log(f"Found {targets.sum()} goals to explore")
        return targets.any(), targets

    def after_search(self, targets, path):
        if path is None:
            self.log("Didn't find any goals.")
            self.kernel().curLevel().explored = True

    def execute(self, path):
        *tail, one = path
        assert one == (self.hero.x, self.hero.y)

        # move towards the exploration goal, unless we're there
        if not tail:  # XXX the original could fail with IndexError
            raise RuntimeError

        self.draw_path(path, color=COLOR_BG_BLUE)
        self.hero.move(tail[-1])

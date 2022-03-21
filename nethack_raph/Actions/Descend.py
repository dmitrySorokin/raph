import numpy as np

from nethack_raph.Actions.base import BaseAction
from nethack_raph.myconstants import COLOR_BG_GREEN


class Descend(BaseAction):
    def can(self, level):
        if self.hero.levitating:  # cant descend while levitating
            return False, np.zeros(level.shape, dtype=bool)

        if self.hero.xp < self.hero.level_number*5:
            return False, np.zeros(level.shape, dtype=bool)

        stairs = level.tiles.char == '>'
        self.log(f"Found {stairs.sum()} stairs")
        return stairs.any(), stairs

    def execute(self, path):
        *tail, one = path
        assert one == (self.hero.x, self.hero.y)
        if tail:
            self.log("Going towards stairs")
            self.draw_path(path, color=COLOR_BG_GREEN)
            self.hero.move(tail[-1])
            return

        if self.kernel().curTile().char != '>':
            self.log('door is absent')
            self.kernel().send(' ')

            # XXX raise False?
            return

        self.hero.descend()

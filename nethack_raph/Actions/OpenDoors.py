import numpy as np

from nethack_raph.Actions.base import BaseAction
from nethack_raph.myconstants import COLOR_BG_CYAN


class OpenDoors(BaseAction):
    mask = np.array([
        [0, 1, 0],
        [1, 0, 1],
        [0, 1, 0],
    ], dtype=bool)

    def can(self, level):
        # all unexplored, walkable neighbours of closed door
        doors = ((
                level.neighbours.is_closed_door &
                ~ level.neighbours.shopkeep_door
        ) & self.mask)

        if self.hero.levitating:  # cant kick while levitating
            doors &= ~level.neighbours.locked

        doors = doors.any((-1, -2))
        doors &= level.tiles.walkable_tile & level.tiles.explored

        self.log(f"found door: {doors.sum() > 0}, {doors.nonzero()}")
        return doors.any(), doors

    def execute(self, path):
        *tail, one = path
        hero = self.hero
        assert one == (hero.x, hero.y)

        if tail:  # not there yet
            self.draw_path(path, color=COLOR_BG_CYAN)
            hero.move(tail[-1])
            return

        # are we next to a door?
        neighbours = self.kernel().curLevel().neighbours[hero.x, hero.y]
        for tile in neighbours[neighbours.is_closed_door]:
            if tile.locked:
                hero.kick(tuple(tile.xy))
            else:
                hero.open(tuple(tile.xy))

            return

        self.log('door is absent')
        self.kernel().send(' ')

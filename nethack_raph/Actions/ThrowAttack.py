from nethack_raph.Actions.base import BaseAction
from nethack_raph.myconstants import RL_VIEW_DISTANCE

import numpy as np


def get_way(array, start, end):
    """
    Returns slice with tiles on the way from point start to point end.
    start and end should be on the same horizontal / vertical or diagonal

    Parameters
    ----------
    array : array_like,
    start : tuple[int, int]
        start point
    end : tuple[int, int]
        end point

    Returns
    -------
    array-like - tiles on the way from point start to point end

    Raises
    ------
    RuntimeError
        when start and end aren't on the same horizontal, vertical or diagonal
    """

    assert start != end

    start_x, start_y = start
    end_x, end_y = end

    if start_x == end_x:  # horizontal
        if start_y < end_y:
            return array[start_x, start_y: end_y + 1]
        else:
            return array[start_x, end_y: start_y + 1][::-1]

    elif start_y == end_y:  # vertical
        if start_x < end_x:
            return array[start_x: end_x + 1, start_y]
        else:
            return array[end_x: start_x + 1, start_y][::-1]

    elif abs(start_x - end_x) == abs(start_y - end_y):  # diagonal
        length = abs(start_x - end_x) + 1
        if (start_x - end_x) * (start_y - end_y) > 0:  # our way is parallel to main diagonal
            if start_x < end_x:
                return np.diagonal(array[start_x:, start_y:])[:length]
            else:
                return np.diagonal(array[end_x:, end_y:])[length-1::-1]

        else:  # our way is parallel to main anti-diagonal
            if start_x < end_x:
                return np.diagonal(np.fliplr(array[start_x:, :start_y + 1]))[:length]
            else:
                return np.diagonal(np.fliplr(array[end_x:, :end_y + 1]))[length-1::-1]

    else:
        raise RuntimeError


def range_attack_candidates(hero, level):
    monsters = []
    for xy, monster in level.monsters.items():
        if monster is None or (not monster.is_attackable and not monster.passive):
            continue

        if xy[0] != hero.x and xy[1] != hero.y \
                and abs(xy[0] - hero.x) != abs(xy[1] - hero.y):
            continue  # not on the same row, file or diagonal

        distance = max(abs(c - h) for c, h in zip(xy, hero.coords()))
        if monster.explosive and distance == 1:
            continue  # don't attack explosion monster nearby

        if distance == 0:
            continue

        way = get_way(level.tiles, hero.coords(), xy)
        if not way[1:-1].walkable_glyph.all():
            continue

        monster_on_the_way = False
        for tile in way[1:-1]:
            if tuple(tile.xy) in level.monsters:
                monster_on_the_way = True
                break

        if monster_on_the_way:
            continue

        dir = tuple(way[1].xy)
        monsters.append((monster, dir, distance))

    return monsters


class ThrowAttack(BaseAction):
    def __init__(self, kernel):
        self.weapon_letter = None
        self.attack_direction = None
        self.exp_damage = None
        super().__init__(kernel)

    def can(self, level):
        if not self.kernel().hero.use_range_attack:
            return False, None

        self.weapon_letter, self.exp_damage = self.kernel().inventory.item_to_throw()
        if self.weapon_letter is None:
            return False, None

        max_range = self.hero.strength // 2

        monsters = range_attack_candidates(self.hero, level)

        closest_dist = 2^16
        attack_dir = None
        for monster, dir, distance in monsters:
            if self.hero.prefer_melee_attack and distance == 1 and (not monster.passive):
                continue

            if distance > max_range:
                continue  # too far away from us

            if distance < closest_dist:
                closest_dist = distance
                attack_dir = dir

        if attack_dir:
            self.attack_direction = attack_dir
            return True, None
        else:
            return False, None

    def execute(self, tile):
        self.hero.throw(tile, self.weapon_letter)

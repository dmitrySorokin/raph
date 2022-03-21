from nethack_raph.Actions.base import BaseAction
from nethack_raph.Actions.ThrowAttack import range_attack_candidates


class ForceBolt(BaseAction):
    def __init__(self, kernel):
        self.attack_direction = None
        self.exp_damage = 13
        super().__init__(kernel)

    def can(self, level):
        if not self.kernel().hero.use_range_attack:
            return False, None

        if not 'force_bolt' in self.hero.spells:
            return False, None

        if self.hero.curpw < 5:
            return False, None

        if self.hero.curhp > self.hero.maxhp * .6 and self.hero.xp > 1:
            return False, None

        monsters = range_attack_candidates(self.hero, level)

        closest_dist = 2^16
        attack_dir = None
        for monster, dir, distance in monsters:
            if self.hero.prefer_melee_attack and distance == 1:
                continue

            if distance < closest_dist:
                closest_dist = distance
                attack_dir = dir

        if attack_dir:
            self.attack_direction = attack_dir
            return True, None
        else:
            return False, None

    def execute(self, path=None):
        self.hero.cast_dir_spell(self.attack_direction, self.hero.spells['force_bolt'])

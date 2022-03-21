from nethack_raph.Actions.base import BaseAction
from nethack_raph.Actions.ThrowAttack import range_attack_candidates
from nethack_raph.myconstants import RL_VIEW_DISTANCE


class LaunchAttack(BaseAction):
    def __init__(self, kernel):
        self.launcher_letter = None
        self.missile_letter = None
        self.attack_direction = None
        self.exp_damage = None
        super().__init__(kernel)

    def can(self, level):
        if not self.kernel().hero.use_launchers:
            return False, None

        self.launcher_letter, self.missile_letter, self.exp_damage = self.kernel().inventory.launcher_missile_pair()
        if self.launcher_letter is None:
            return False, None

        max_range = self.hero.strength // 2 + 1

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
        self.hero.launch(tile, self.launcher_letter, self.missile_letter)

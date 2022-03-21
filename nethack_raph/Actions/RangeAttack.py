from nethack_raph.Actions.base import BaseAction
from nethack_raph.Actions.ForceBolt import ForceBolt
from nethack_raph.Actions.LaunchAttack import LaunchAttack
from nethack_raph.Actions.ThrowAttack import ThrowAttack

import numpy as np


class RangeAttack(BaseAction):
    def __init__(self, kernel):
        self.throw_action = ThrowAttack(kernel)
        self.launch_action = LaunchAttack(kernel)
        self.forcebolt_action = ForceBolt(kernel)
        self.action_to_do = None
        self.exp_damage = 0
        super().__init__(kernel)

    def can(self, level):
        can_throw, _ = self.throw_action.can(level)
        can_launch, _ = self.launch_action.can(level)
        can_forcebolt, _ = self.forcebolt_action.can(level)

        actions = [
            (can_throw, self.throw_action.exp_damage, 'throw'),
            (can_launch, self.launch_action.exp_damage, 'launch'),
            (can_forcebolt, self.forcebolt_action.exp_damage, 'force_bolt'),
        ]

        if not any([can for can, exp_damage, name in actions]):
            return False, None

        _, self.exp_damage, self.action_to_do = max(
            actions,
            key=lambda x: x[1] if x[0] else -np.inf    # exp_damage if can else -inf
        )
        return True, None

    def execute(self, path=None):
        if self.action_to_do == 'throw':
            self.throw_action.execute(path)
        elif self.action_to_do == 'launch':
            self.launch_action.execute(path)
        elif self.action_to_do == 'force_bolt':
            self.forcebolt_action.execute(path)
        else:
            raise Exception

from nethack_raph.Actions.base import BaseAction
from nethack_raph.myconstants import RL_VIEW_DISTANCE


class RLTriggerAction(BaseAction):
    def can(self, level):

        if self.hero.isEngulfed:
            return True, None

        currx, curry = self.kernel().hero.coords()

        def dist_form_current(xy):
            tx, ty = xy
            return max(abs(tx - currx), abs(ty - curry))

        for xy, m in level.monsters.items():
            if (m.is_attackable or m.passive) and dist_form_current(xy) <= RL_VIEW_DISTANCE:
                return True, None

        return False, None

    def execute(self, path):
        assert False

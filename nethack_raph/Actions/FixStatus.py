import numpy as np

from nethack_raph.Actions.base import BaseAction


class FixStatus(BaseAction):
    def can(self, level):
        if self.hero.blind or self.hero.isLycanthropy:
            return True, None

        return False, None

    def execute(self, path=None):
        assert path is None
        # XXX what is five?
        self.hero.search(5)

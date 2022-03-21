from nethack_raph.Actions.base import BaseAction


class Enhance(BaseAction):
    def can(self, level):
        if not sum(self.hero.skills.values()) or self.hero.can_enhance:
            return True, None

        return False, None

    def execute(self, path=None):
        self.hero.enhance()

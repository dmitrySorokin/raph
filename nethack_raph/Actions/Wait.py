from nethack_raph.Actions.base import BaseAction


class Wait(BaseAction):
    def can(self, level):
        return True, None

    def execute(self, path=None):
        self.kernel().hero.search(60)

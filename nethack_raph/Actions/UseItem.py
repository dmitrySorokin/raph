from nethack_raph.Actions.base import BaseAction


class UseItem(BaseAction):
    def __init__(self, kernel):
        self.action_to_do = None
        super().__init__(kernel)

    def can(self, level):
        if self.kernel().inventory.healing_potions:
            self.action_to_do = 'quaff'
            return True, None

        return False, None

    def execute(self, path=None):
        if self.action_to_do == 'quaff':
            potion_letter = self.kernel().inventory.healing_potions.pop(0)
            self.hero.quaff(potion_letter)
            return

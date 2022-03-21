from nethack_raph.Actions.base import BaseAction


class Elbereth(BaseAction):
    def can(self, level):
        # hp is at an acceptable level
        hero = self.hero
        if hero.curhp >= hero.maxhp / 2:
            return False, None

        # we are staying on elbereth sign already
        tile = level.tiles[hero.x, hero.y]
        if hero.lastAction == 'read' and tile.has_elbereth:
            self.log("We are staying on elbereth sign already")
            return False, None

        # can't write on the fountains
        if tile.char in ['{', '}']:
            return False, None

        # too hard to write while blinded / confused / stunned, etc.
        if any([
            hero.blind,
            hero.confused,
            hero.stun,
            hero.hallu,
            hero.levitating,
            hero.isEngulfed,
            hero.isLycanthropy,
        ]):
            return False, None

        # monsters with elbereth disrespect or range attack
        bad_monsters = [
            m for m in level.monsters.values()
            if m.is_attackable and (not m.respect_elbereth or m.range_attack)
        ]
        if bad_monsters:
            self.log("Beware, there is a monster with elbereth disrespect or range attack")
            return False, None

        return True, None

    def execute(self, path=None):
        assert path is None
        self.hero.write()

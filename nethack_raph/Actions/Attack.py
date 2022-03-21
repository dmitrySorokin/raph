import numpy as np

from nethack_raph.Actions.base import BaseAction


class Attack(BaseAction):
    def __init__(self, kernel):
        self.exp_damage = 0
        super().__init__(kernel)

    def can(self, level):
        monsters = np.zeros(level.shape, dtype=bool)
        self.exp_damage = self.kernel().inventory.current_exp_melee_attack()
        currx, curry = self.kernel().hero.coords()

        if self.hero.isEngulfed:
            monsters[:] = True
            monsters[(currx, curry)] = False
            self.log("Attacking while engulfed..")
            return True, monsters

        neighbours = level.neighbours[self.hero.x, self.hero.y].xy.flat
        neib_monsters = [
            level.monsters[xy] for xy in map(tuple, neighbours)
            if xy in level.monsters and (level.monsters[xy].is_attackable or level.monsters[xy].passive)
        ]
        if not neib_monsters:
            self.exp_damage *= 0

        for xy, m in level.monsters.items():
            if m.is_attackable or m.passive:
                monsters[xy] = True
                self.log(f"Found monster {xy}: {str(m)}")

        return monsters.any(), monsters

    def execute(self, tile):
        lvl = self.kernel().curLevel()

        if self.hero.isEngulfed:
            targets = list(lvl.adjacent(lvl.tiles[self.hero.coords()]))
            xy = tuple(np.random.choice(targets).xy)
            self.hero.attack(xy)
            return

        monster = lvl.monsters.get(tile)
        if monster and (monster.is_attackable or monster.passive):
            self.hero.attack(tile)
        else:
            self.hero.move(tile)

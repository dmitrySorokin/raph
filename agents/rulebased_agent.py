from agents.base import BatchedAgent
from nethack_raph.Pathing import dijkstra_cpp
from nethack_raph.rl_wrapper import StateValues, RLActions, DIRECTIONS
import numpy as np


def sign(value):
    if value == 0:
        return 0
    elif value > 0:
        return 1
    else:
        return -1


def _get_direction_id(x, y):
    for i, (off_x, off_y) in enumerate(DIRECTIONS):
        if x == off_x and y == off_y:
            return i
    return None


class RuleBasedAgent(BatchedAgent):
    def __init__(self, num_envs, num_actions):
        super(RuleBasedAgent, self).__init__(num_envs, num_actions)

    def range_attack(self, monsters, hero_x, hero_y):
        directions_with_dist = []
        for (x, y) in zip(*np.where(monsters)):
            x_dist, y_dist = x - hero_x, y - hero_y
            dist = max(abs(x_dist), abs(y_dist))
            if abs(x_dist) == abs(y_dist) or x_dist == 0 or x_dist == 0:
                dir_id = _get_direction_id(sign(x_dist), sign(y_dist))
                if dir_id is not None:
                    directions_with_dist.append((dir_id, dist))
        if not directions_with_dist:
            return None
        return min(directions_with_dist, key=lambda item: item[1])[0]

    def mellee_attack(self, dungeon, monsters, hero_x, hero_y):
        # We are adjacent to monster. So we can attack diagonally through doorway
        for (x, y) in zip(*np.where(monsters)):
            dir_id = _get_direction_id(x - hero_x, y - hero_y)
            if dir_id is not None:
                return dir_id

        # Find path through walkable tiles. It wont go diagonally through doorways
        walk_costs = dungeon[StateValues.WALKABLE_TILE].astype(np.float)
        walk_costs[walk_costs == 0] = np.inf
        doors = dungeon[StateValues.IS_OPENED_DOOR]
        path = dijkstra_cpp(walk_costs, (hero_x, hero_y), monsters, doors)
        if path is None:
            return None

        *tail, one = path
        assert one == (hero_x, hero_y)
        assert len(tail) >= 1
        x, y = tail[-1]
        return _get_direction_id(x - hero_x, y - hero_y)

    def act(self, obs):
        if not obs['rl_triggered']:
            return RLActions.CONTINUE

        action_mask = obs['action_mask']

        if action_mask[RLActions.ELBERETH]:
            return RLActions.ELBERETH

        if action_mask[RLActions.PRAY]:
            return RLActions.PRAY

        dungeon = obs['map']
        hero_y, hero_x = obs['blstats'][:2]
        monsters = np.bitwise_or(dungeon[StateValues.IS_ATTACKABLE], dungeon[StateValues.PASSIVE])
        range_dir = self.range_attack(monsters, hero_x, hero_y)
        if range_dir is not None and action_mask[RLActions.RANGE_ATTACK_BEGIN + range_dir]:
            return RLActions.RANGE_ATTACK_BEGIN + range_dir

        mellee_dir = self.mellee_attack(dungeon, monsters, hero_x, hero_y)
        if mellee_dir is not None and action_mask[RLActions.MELLEE_ATTACK_BEGIN + mellee_dir]:
            return RLActions.MELLEE_ATTACK_BEGIN + mellee_dir

        assert action_mask[RLActions.WAIT]
        return RLActions.WAIT

    def batched_step(self, observations, rewards, dones, infos):
        return [self.act(obs) for obs in observations]

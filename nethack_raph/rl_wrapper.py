import enum

from nethack_raph.Kernel import Kernel
from nethack_raph.myconstants import DUNGEON_HEIGHT, DUNGEON_WIDTH
from nethack_raph.Actions.RLTriggerAction import RLTriggerAction

import gym
import numpy as np
from nle import nethack as nh
from nle.nethack.actions import ACTIONS


class StateValues(enum.IntEnum):
    EXPLORED = 0
    WALKABLE_TILE = 1
    WALKABLE_GLYPH = 2
    IS_HERO = 3
    IS_OPENED_DOOR = 4
    IS_CLOSED_DOOR = 5
    IN_SHOP = 6
    SHOP_ENTRANCE = 7
    LOCKED = 8
    HAS_ELBERETH = 9
    IS_MONSTER = 10
    IS_ATTACKABLE = 11
    PASSIVE = 12
    EXPLOSIVE = 13
    RESPECT_ELBERETH = 14
    PEACEFUL = 15
    RANGE_ATTACK = 16
    ARMOR_CLASS = 17
    M_LEVEL = 18
    M_MOVE = 19


class RLActions(enum.IntEnum):
    CONTINUE = -1
    WAIT = 16,
    ELBERETH = 17,
    PRAY = 18
    RANGE_ATTACK_BEGIN = 8
    RANGE_ATTACK_END = 16
    MELLEE_ATTACK_BEGIN = 0
    MELLEE_ATTACK_END = 8


DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]


class RLWrapper(gym.Wrapper):
    def __init__(self, env, verbose=False, early_stop=1900):
        super().__init__(env)
        self.verbose = verbose
        self.early_stop = early_stop
        self.kernel = Kernel(verbose=self.verbose, early_stop=early_stop)

        self.action_space = gym.spaces.Discrete(19)
        self.action2id = {
            chr(action.value): action_id for action_id, action in enumerate(ACTIONS)
        }

        self.episode_reward = 0
        self.is_corner = [False, False, False, False, True, True, True, True]
        self.roles = np.array(['arc', 'bar', 'cav', 'hea', 'kni', 'mon', 'pri', 'ran', 'rog', 'sam', 'tou', 'val', 'wiz'])
        self.races = np.array(['dwa', 'elf', 'gno', 'hum', 'orc'])
        self.genders = np.array(['fem', 'mal'])
        self.morals = np.array(['cha', 'law', 'neu'])
        self.last_obs = None
        self.reward = 0

        self.actionid2name = {RLActions.CONTINUE: 'Continue'}
        for i in range(RLActions.MELLEE_ATTACK_BEGIN, RLActions.MELLEE_ATTACK_END):
            self.actionid2name[i] = 'Attack'
        for i in range(RLActions.RANGE_ATTACK_BEGIN, RLActions.RANGE_ATTACK_END):
            self.actionid2name[i] = 'RangeAttack'
        self.actionid2name[RLActions.WAIT] = 'Wait'
        self.actionid2name[RLActions.ELBERETH] = 'Elbereth'
        self.actionid2name[RLActions.PRAY] = 'Pray'

    def reset(self):
        self.reward = 0
        del self.kernel
        self.kernel = Kernel(verbose=self.verbose, early_stop=self.early_stop)
        self.last_obs = self.env.reset()
        self.kernel.update(self.last_obs)
        _, _, done, _ = self._step()
        if done:
            return self.reset()
        return self._process_obs(self.last_obs, rl_triggered=False)

    def step(self, action_id):
        self.reward = 0

        action_id = int(action_id)
        action_name = self.actionid2name[action_id]
        if action_name in ('Attack', 'RangeAttack'):
            x, y = self.kernel.hero.coords()
            tile_x, tile_y = DIRECTIONS[action_id % 8]
            tile = (tile_x + x, tile_y + y)
            self.kernel.brain.rl_actions[action_name].execute(tile)
        elif action_name in ('Wait', 'Elbereth', 'Pray'):
            self.kernel.brain.rl_actions[action_name].execute()
        else:
            action, path = self.kernel.brain.execute_next(self.kernel.curLevel())
            if isinstance(action, RLTriggerAction):
                return self._process_obs(self.last_obs, rl_triggered=True), self.reward, False, {}
            action.execute(path)

        assert len(self.kernel.action) > 0
        self.last_obs, _, done, info = self._step()
        return self._process_obs(self.last_obs, rl_triggered=False), self.reward, done, info

    def _step(self):
        done, info = False, {}
        while not done and self.kernel.action:
            self.last_obs, rew, done, info = self.env.step(self.action2id.get(self.kernel.action[0]))
            self.reward += rew
            self.kernel.action = self.kernel.action[1:]
            if self.kernel.action:
                continue
            self.kernel.update(self.last_obs)

        info['role'] = self.kernel.hero.role
        return self.last_obs, self.reward, done, info

    def _process_obs(self, obs, rl_triggered):
        state = np.zeros((24, DUNGEON_HEIGHT, DUNGEON_WIDTH), dtype=np.int32)
        action_mask = np.zeros(self.action_space.n, dtype=np.float32)

        if not rl_triggered:
            return {
                'map': state,
                'message': obs['message'],
                'blstats': obs['blstats'],
                'action_mask': action_mask,
                'hero_stat': np.zeros(26),
                'rl_triggered': rl_triggered,
            }

        lvl = self.kernel.curLevel()
        tiles = lvl.tiles
        state[StateValues.EXPLORED] = tiles.explored
        state[StateValues.WALKABLE_TILE] = tiles.walkable_tile
        state[StateValues.WALKABLE_GLYPH] = tiles.walkable_glyph
        state[StateValues.IS_HERO] = tiles.is_hero
        state[StateValues.IS_OPENED_DOOR] = tiles.is_opened_door
        state[StateValues.IS_CLOSED_DOOR] = tiles.is_closed_door
        state[StateValues.IN_SHOP] = tiles.in_shop
        state[StateValues.SHOP_ENTRANCE] = tiles.shop_entrance
        state[StateValues.LOCKED] = tiles.locked
        state[StateValues.HAS_ELBERETH] = tiles.has_elbereth

        for (x, y), monster in lvl.monsters.items():
            state[StateValues.IS_MONSTER, x, y] = True
            state[StateValues.IS_ATTACKABLE, x, y] = monster.is_attackable
            state[StateValues.PASSIVE, x, y] = monster.passive
            state[StateValues.EXPLOSIVE, x, y] = monster.explosive
            state[StateValues.RESPECT_ELBERETH, x, y] = monster.respect_elbereth
            state[StateValues.PEACEFUL, x, y] = monster.peaceful
            state[StateValues.RANGE_ATTACK, x, y] = monster.range_attack
            if monster.glyph < 381:
                mon_info = nh.permonst(nh.glyph_to_mon(monster.glyph))
                state[StateValues.ARMOR_CLASS, x, y] = mon_info.ac
                state[StateValues.M_LEVEL, x, y] = mon_info.mlevel
                state[StateValues.M_MOVE, x, y] = mon_info.mmove

        x, y = self.kernel.hero.coords()
        doors = lvl.tiles.is_opened_door

        for i, off in enumerate(DIRECTIONS):
            tile = (x + off[0], y + off[1])
            if tile[0] < 0 or tile[0] >= DUNGEON_HEIGHT or tile[1] < 0 or tile[1] >= DUNGEON_WIDTH:
                continue

            if tile in lvl.monsters:
                action_mask[i] = 1.0

            if self.is_corner[i] and (doors[tile] or doors[(x, y)]):
                continue

            if tiles[tile].walkable_tile:
                action_mask[i] = 1.0

        if self.kernel.brain.rl_actions['RangeAttack'].can(lvl)[0]:
            action_mask[RLActions.RANGE_ATTACK_BEGIN:RLActions.RANGE_ATTACK_END] = 1.0
        if self.kernel.brain.rl_actions['Wait'].can(lvl)[0]:
            action_mask[RLActions.WAIT] = 1.0
        if self.kernel.brain.rl_actions['Elbereth'].can(lvl)[0]:
            action_mask[RLActions.ELBERETH] = 1.0
        if self.kernel.brain.rl_actions['Pray'].can(lvl)[0]:
            action_mask[RLActions.PRAY] = 1.0

        self.kernel.brain.rl_actions['Attack'].can(lvl)  # exp_damage update
        hero_stat = np.concatenate([
            self.kernel.hero.role == self.roles,
            self.kernel.hero.race == self.races,
            self.kernel.hero.gender == self.genders,
            self.kernel.hero.moral == self.morals,
            [
                self.kernel.hero.prefer_melee_attack,
                self.kernel.brain.rl_actions['Attack'].exp_damage / 10.,
                self.kernel.brain.rl_actions['RangeAttack'].exp_damage / 10.
            ]
        ]).astype(np.float32)

        range_inventory = self.kernel.inventory.item_to_throw()[0] is not None
        range_inventory |= self.kernel.inventory.launcher_missile_pair()[0] is not None

        return {
            'map': state,
            'message': obs['message'],
            'blstats': obs['blstats'],
            'action_mask': action_mask,
            'hero_stat': hero_stat,
            'rl_triggered': rl_triggered,
            'inventory': np.array([range_inventory])
        }

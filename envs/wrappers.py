import aicrowd_gym
import nle
from gym.wrappers import TimeLimit
import gym
from nethack_raph.rl_wrapper import RLWrapper
from nle.nethack import ACTIONS
import numpy as np


def create_env(character='@'):
    """This is the environment that will be assessed by AIcrowd."""
    return aicrowd_gym.make("NetHackChallenge-v0", character=character)


def addtimelimitwrapper_fn(character='@'):
    """
    An example of how to add wrappers to the nethack_make_fn
    Should return a gym env which wraps the nethack gym env
    """
    env = create_env(character=character)
    env = TimeLimit(env, max_episode_steps=10_000_000)
    return env


def addtimelimitwrapper_fn_custom(character='@', verbose=False):
    env = addtimelimitwrapper_fn(character)
    env = InfoWrapper(env)
    return env


def addtimelimitwrapper_fn_rl(character='@', verbose=False):
    env = addtimelimitwrapper_fn(character)
    env = RLWrapper(env, verbose=verbose)
    return env


def minihack_task(task='MiniHack-CorridorBattle-v0', character='@', verbose=False):
    import minihack
    env = gym.make(task, character=character, actions=ACTIONS)
    env = MinihackWrapper(env)
    env = RLWrapper(env, verbose=verbose)
    return env


class InfoWrapper(gym.Wrapper):
    def __init__(self, env):
        self.env = env
        self.episode_reward = 0
        self.action_space = env.action_space

    def reset(self):
        self.episode_reward = 0
        obs = self.env.reset()
        return obs

    def step(self, action):
        obs, reward, done, info = self.env.step(action)
        self.episode_reward += reward

        if done:
            info['episode'] = {'r': self.episode_reward}
            info['role'] = '@'

        return obs, reward, done, info


class MinihackWrapper(gym.ObservationWrapper):
    def observation(self, observation):
        tty_chars = np.zeros((24, 80), dtype=np.uint8)
        tty_chars[1:-2, :-1] = observation['chars']

        tty_colors = np.zeros((24, 80), dtype=np.uint8)
        tty_colors[1:-2, :-1] = observation['colors']

        observation['tty_chars'] = tty_chars
        observation['tty_colors'] = tty_colors

        observation['inv_glyphs'] = np.array([1970])

        observation['inv_strs'] = np.zeros((1, 80), dtype=np.uint8)
        inv_str = np.frombuffer('a +2 bullwhip (weapon in hand)'.encode('ascii'), dtype=np.uint8)
        observation['inv_strs'][0, 0:len(inv_str)] = inv_str
        observation['inv_letters'] = np.array([ord('a')])
        observation['inv_oclasses'] = np.array([2])

        observation['misc'] = np.zeros(3, dtype=np.uint8)

        return observation

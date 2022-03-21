import gym
import numpy as np

from agents.torchbeast_agent import TorchBeastAgent
from agents.random_agent import RandomAgent
from agents.rulebased_agent import RuleBasedAgent
from submission_config import SubmissionConfig


from rollout import run_batched_rollout
from envs.batched_env import BatchedEnv
from envs.wrappers import RLWrapper, MinihackWrapper, ACTIONS
import minihack

from nle_toolbox.wrappers.replay import ReplayToFile


def evaluate(seed, character):
    # env = gym.make('MiniHack-CorridorBattle-v0', character=character, actions=ACTIONS)
    # env = MinihackWrapper(env)

    env = SubmissionConfig.MAKE_ENV_FN(character=character, verbose=True)
    env = ReplayToFile(env, folder='./replays', save_on='close,done')
    # env = RLWrapper(env, verbose=True)

    # ensure seed prior to making a lambda factory
    if seed is not None:
        env.seed(seed=tuple(seed))

    Agent = SubmissionConfig.AGENT
    batched_env = BatchedEnv(env_make_fn=lambda: env, num_envs=1)
    agent = Agent(1, batched_env.num_actions)

    ascensions, scores = run_batched_rollout(1, batched_env, agent)

    print(
        f"Ascensions: {ascensions} "
        f"Median Score: {np.median(scores)}, "
        f"Mean Score: {np.mean(scores)}"
    )
    return np.median(scores)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Interactively replay a recorded playthrough.',
        add_help=True)

    parser.add_argument(
        '--seed', type=int, nargs=2, required=False, dest='seed',
        help='The seed pair to use. See `python -m nle_toolbox.utils.play replay.pkl`.',
    )

    parser.add_argument('--character', default='@')

    parser.set_defaults(seed=None)

    args, _ = parser.parse_known_args()
    evaluate(**vars(args))

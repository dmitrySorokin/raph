import numpy as np
from submission_config import SubmissionConfig, TestEvaluationConfig
from rollout import run_batched_rollout
from envs.batched_env import BatchedEnv
from envs.wrappers import create_env, TimeLimit
from nethack_raph.rl_wrapper import RLWrapper

from nle_toolbox.wrappers.replay import ReplayToFile


def env_make_fn(verbose=False):
    env = create_env()
    env = ReplayToFile(env, folder='test_new', sticky=False)  # should be before RLWrapper
    env = TimeLimit(env, max_episode_steps=10_000_000)
    env = RLWrapper(env, verbose=verbose, early_stop=np.inf)
    return env


def evaluate():
    num_envs = 8
    Agent = SubmissionConfig.AGENT

    num_episodes = 4096

    batched_env = BatchedEnv(env_make_fn=env_make_fn, num_envs=num_envs)

    agent = Agent(num_envs, batched_env.num_actions)

    ascensions, scores = run_batched_rollout(num_episodes, batched_env, agent)
    print(
        f"Ascensions: {ascensions} "
        f"Median Score: {np.median(scores)}, "
        f"Mean Score: {np.mean(scores)}"
    )
    return np.median(scores)


if __name__ == "__main__":
    evaluate()

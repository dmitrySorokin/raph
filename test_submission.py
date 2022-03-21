## This file is intended to emulate the evaluation on AIcrowd

# IMPORTANT - Differences to expect
# * All the environment's functions are not available
# * The run might be slower than your local run
# * Resources might vary from your local machine

import numpy as np

from submission_config import SubmissionConfig, TestEvaluationConfig

from rollout import run_batched_rollout
from envs.wrappers import addtimelimitwrapper_fn
from envs.batched_env import BatchedEnv


def evaluate():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--character', default='@')
    parser.add_argument('--num-environments', default=SubmissionConfig.NUM_ENVIRONMENTS, type=int)
    parser.add_argument('--num-episodes', default=TestEvaluationConfig.NUM_EPISODES, type=int)

    args = parser.parse_args()

    num_envs = args.num_environments
    num_episodes = args.num_episodes

    env_make_fn = SubmissionConfig.MAKE_ENV_FN
    if args.character != '@':
        env_make_fn = lambda: SubmissionConfig.MAKE_ENV_FN(args.character)

    Agent = SubmissionConfig.AGENT

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

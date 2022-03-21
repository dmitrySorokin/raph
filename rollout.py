#!/usr/bin/env python

################################################################
## Ideally you shouldn't need to change this file at all      ##
##                                                            ##
## This file generates the rollouts, with the specific agent, ##
## batch_size and wrappers specified in subminssion_config.py ##
################################################################
from collections import defaultdict
from tqdm import tqdm
import numpy as np

from envs.batched_env import BatchedEnv
from envs.wrappers import create_env
from submission_config import SubmissionConfig



def run_batched_rollout(num_episodes, batched_env, agent):
    """
    This function will generate a series of rollouts in a batched manner.
    """

    num_envs = batched_env.num_envs

    # This part can be left as is
    observations = batched_env.batch_reset()
    rewards = [0.0 for _ in range(num_envs)]
    dones = [False for _ in range(num_envs)]
    infos = [{} for _ in range(num_envs)]

    # We mark at the start of each episode if we are 'counting it'
    active_envs = [i < num_episodes for i in range(num_envs)]
    num_remaining = num_episodes - sum(active_envs)
    
    episode_count = 0
    pbar = tqdm(total=num_episodes)

    ascension_count = 0
    all_returns = []
    role_stats = defaultdict(list)
    returns = [0.0 for _ in range(num_envs)]
    # The evaluator will automatically stop after the episodes based on the development/test phase
    while episode_count < num_episodes:
        actions = agent.batched_step(observations, rewards, dones, infos)
        observations, rewards, dones, infos = batched_env.batch_step(actions)

        for i, r in enumerate(rewards):
            returns[i] += r
        
        for done_idx in np.where(dones)[0]:
            if active_envs[done_idx]:
                # We were 'counting' this episode
                episode_count += 1
                all_returns.append(returns[done_idx])
                
                active_envs[done_idx] = (num_remaining > 0)
                num_remaining -= 1
                
                ascension_count += int(infos[done_idx]["is_ascended"])

                role = infos[done_idx]['role']
                role_stats[role].append(returns[done_idx])

                pbar.update(1)
            
            returns[done_idx] = 0.0
    pbar.close()

    for role, r_scores in sorted(role_stats.items()):
        print(role, int(np.median(r_scores)), int(np.mean(r_scores)), len(r_scores))

    return ascension_count, all_returns

if __name__ == "__main__":
    # AIcrowd will cut the assessment early duing the dev phase
    NUM_ASSESSMENTS = 4096

    env_make_fn = SubmissionConfig.MAKE_ENV_FN
    num_envs = SubmissionConfig.NUM_ENVIRONMENTS
    Agent = SubmissionConfig.AGENT


    batched_env = BatchedEnv(env_make_fn=env_make_fn, num_envs=num_envs)
    agent = Agent(num_envs, batched_env.num_actions)

    run_batched_rollout(NUM_ASSESSMENTS, batched_env, agent)

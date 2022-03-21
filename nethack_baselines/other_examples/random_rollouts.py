# This is intended as an example of a barebones submission
# Do not that not using BatchedEnv not meet the timeout requirement.

import aicrowd_gym
import nle

def main():
    """
    This function will be called for training phase.
    """

    # This allows us to limit the features of the environment 
    # that we don't want participants to use during the submission
    env = aicrowd_gym.make("NetHackChallenge-v0") 

    env.reset()
    done = False
    episode_count = 0
    while episode_count < 200:
        _, _, done, _ = env.step(env.action_space.sample())
        if done:
            episode_count += 1
            print(episode_count)
            env.reset()

if __name__ == "__main__":
    main()

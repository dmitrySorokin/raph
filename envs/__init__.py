from gym.envs.registration import register

register('NetHackChallengeBatched-v0', 
            entry_point='nle_batched_env.NetHackChallengeBatchedEnv')

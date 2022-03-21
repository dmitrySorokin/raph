import torch
import numpy as np
from collections import defaultdict

from agents.base import BatchedAgent

from nethack_baselines.torchbeast.models import load_model
from nethack_raph.rl_wrapper import RLActions

MODEL_DIR = "./latest/"


class TorchBeastAgent(BatchedAgent):
    """
    A BatchedAgent using the TorchBeast Model
    """

    def __init__(self, num_envs, num_actions):
        super().__init__(num_envs, num_actions)
        self.model_dir = MODEL_DIR
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.model = load_model(MODEL_DIR, self.device)
        print(f'Using Model In: {self.model_dir}, Device: {self.device}')

        self.core_state = [
            m.to(self.device) for m in self.model.initial_state(batch_size=num_envs)
        ]

        self.model.eval()

    def batched_step(self, observations, rewards, dones, infos):
        """
        Perform a batched step on lists of environment outputs.

        Torchbeast models:
            * take the core (LSTM) state as input, and return as output
            * return outputs as a dict of "action", "policy_logits", "baseline"
        """

        actions = np.zeros(len(observations))
        rl_action_ids = []
        rl_obs = defaultdict(list)

        for i, obs in enumerate(observations):
            if not obs['rl_triggered']:
                actions[i] = RLActions.CONTINUE
                continue
            rl_action_ids.append(i)
            for key, value in obs.items():
                rl_obs[key].append(value)
            rl_obs['done'].append(dones[i])

        for key in rl_obs:
            rl_obs[key] = torch.Tensor(np.stack(rl_obs[key])[None, ...]).to(self.device)

        if rl_obs:
            with torch.no_grad():
                outputs, self.core_state = self.model(rl_obs, self.core_state)
                rl_actions = outputs["action"].cpu().numpy()[0]

            actions[rl_action_ids] = rl_actions

        return actions

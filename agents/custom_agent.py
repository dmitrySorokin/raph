from agents.base import BatchedAgent
from nethack_raph.Kernel import Kernel

from nle.nethack.actions import ACTIONS
import time

import multiprocessing as mp


class Agent:
    def __init__(self, verbose):
        super().__init__()

        self.action2id = {
            chr(action.value): action_id for action_id, action in enumerate(ACTIONS)
        }
        self.verbose = verbose
        self.kernel = Kernel(verbose=self.verbose)
        self.action_queue = ''

    def reset(self):
        del self.kernel
        self.action_queue = ''
        self.kernel = Kernel(verbose=self.verbose)

    def step(self, obs):
        if not self.action_queue:
            self.action_queue = self.kernel.step(obs)

        if len(self.action_queue):
            ch = self.action_queue[0]
            self.action_queue = self.action_queue[1:]
        else:
            #TODO check if it happens
            ch = ' '

        action = self.action2id.get(ch)
        if action is None:
            #TODO check if it happens
            action = 0
        return action


class Process(mp.Process):
    def __init__(self, remote, parent_remote, daemon=True):
        super().__init__(daemon=daemon)
        self.remote = remote
        self.parent_remote = parent_remote
        self.agent = None

    def run(self):
        self.agent = Agent(verbose=False)
        self.parent_remote.close()
        while True:
            try:
                observation, done = self.remote.recv()
                if done:
                    self.agent.reset()

                action = self.agent.step(observation)
                self.remote.send(action)
            except EOFError:
                break


class SubprocVecEnv:
    def __init__(self, n_processes):
        self.waiting = False

        # Fork is not a thread safe method (see issue #217)
        # but is more user friendly (does not require to wrap the code in
        # a `if __name__ == "__main__":`)
        forkserver_available = "forkserver" in mp.get_all_start_methods()
        start_method = "forkserver" if forkserver_available else "spawn"
        ctx = mp.get_context(start_method)

        self.remotes, self.work_remotes = zip(*[ctx.Pipe() for _ in range(n_processes)])
        self.processes = []
        for work_remote, remote in zip(self.work_remotes, self.remotes):
            # daemon=True: if the main process crashes, we should not cause things to hang
            process = Process(work_remote, remote, daemon=True)  # pytype:disable=attribute-error
            process.start()
            self.processes.append(process)
            work_remote.close()

    def step(self, states, dones):
        self.step_async(states, dones)
        return self.step_wait()

    def step_async(self, states, dones):
        for remote, state, done in zip(self.remotes, states, dones):
            remote.send((state, done))
        self.waiting = True

    def step_wait(self):
        results = [remote.recv() for remote in self.remotes]
        self.waiting = False
        return results

class SubprocVecEnvSimple:
    def __init__(self, n_processes, verbose=False):
        assert n_processes == 1
        self.agent = Agent(verbose=verbose)
        self.maxtime = 0

    def step(self, states, dones):
        assert len(dones) == 1

        if int(dones[0]):
            self.agent.reset()

        before = time.time()
        action = self.agent.step(states[0])
        after = time.time()

        self.maxtime = max(self.maxtime, after - before)
        self.agent.kernel.log(f'action full: {self.agent.kernel.action}')
        self.agent.kernel.log(f'action time: {after - before}, maxtime: {self.maxtime}')
        return [action]


class CustomAgentMP(BatchedAgent):
    def __init__(self, num_envs, num_actions, verbose=False):
        """Set up and load you model here"""
        super().__init__(num_envs, num_actions)
        self.agents = SubprocVecEnv(num_envs)
        if num_envs > 1:
            self.agents = SubprocVecEnv(num_envs)
        else:
            self.agents = SubprocVecEnvSimple(num_envs, verbose)

    def batched_step(self, observations, rewards, dones, infos):
        """
        Perform a batched step on lists of environment outputs.

        Each argument is a list of the respective gym output.
        Returns an iterable of actions.
        """
        return self.agents.step(observations, dones)


class CustomAgent(BatchedAgent):
    """A example agent... that simple acts randomly. Adapt to your needs!"""

    def __init__(self, num_envs, num_actions, *, verbose=False):
        """Set up and load you model here"""
        super().__init__(num_envs, num_actions)
        self.agent = Agent(verbose=verbose)
        self.maxtime = 0
        self.reward = 0

    def batched_step(self, observations, rewards, dones, infos):
        """
        Perform a batched step on lists of environment outputs.

        Each argument is a list of the respective gym output.
        Returns an iterable of actions.
        """

        assert len(dones) == 1
        self.reward += rewards[0]

        if int(dones[0]):
            # input(f'tot reward: {self.reward}')
            self.agent.reset()
            self.reward = 0

        before = time.time()
        action = self.agent.step(observations[0])
        after = time.time()

        self.maxtime = max(self.maxtime, after - before)
        self.agent.kernel.log(f'action full: {self.agent.kernel.action}')
        self.agent.kernel.log(f'action time: {after - before}, maxtime: {self.maxtime}')
        return [action]

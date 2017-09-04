import os
import subprocess
import signal
import time
import numpy as np

from general.algorithm.probcoll import Probcoll
from general.algorithm.probcoll_model import ProbcollModel
from general.algorithm.probcoll_model_replay_buffer import ProbcollModelReplayBuffer
from general.state_info.sample import Sample
from general.policy.random_policy import RandomPolicy
from general.policy.policy_cem import PolicyCem
from robots.sim_rccar.policy.policy_random_planning_sim_rccar import PolicyRandomPlanningSimRCcar
from robots.sim_rccar.agent.agent_sim_rccar import AgentSimRCcar

from config import params

class ProbcollSimRCcar(Probcoll):

    def __init__(self, save_dir=None, data_dir=None):
        Probcoll.__init__(self, save_dir=save_dir, data_dir=data_dir)

    def _setup(self):
        probcoll_params = params['probcoll']
        self._max_iter = probcoll_params['max_iter']
        self.agent = AgentSimRCcar(params['sim'])
        self.agent_testing = AgentSimRCcar(params['sim_testing'])
        self._num_timesteps = params['probcoll']['num_timesteps']
        ### load prediction neural net
#        self.probcoll_model = ProbcollModel(save_dir=self._save_dir, data_dir=self._data_dir)
        self.probcoll_model = ProbcollModelReplayBuffer(save_dir=self._save_dir, data_dir=self._data_dir)

    ##########################
    ### Threaded Functions ###
    ##########################

    def _async_training(self):
        try:
            p = subprocess.Popen(
                ["python", "main.py", "train", "sim_rccar", "--asynch"])
            self._jobs.append(p)
        except Exception as e:
            self._logger.warning('Error starting async training!')
            self._logger.warning(e)

    #########################
    ### Create controller ###
    #########################

    def _create_mpc(self):
        """ Must initialize MPC """
        self._logger.info('\t\t\tCreating MPC')
        if self._planner_type == 'random_policy':
            mpc_policy = RandomPolicy()
        elif self._planner_type == 'random':
            mpc_policy = PolicyRandomPlanningSimRCcar(self.probcoll_model, params['planning'])
        elif self._planner_type == 'cem':
            mpc_policy = PolicyCem(self.probcoll_model, params['planning'])
        else:
            raise NotImplementedError('planner_type {0} not implemented for rccar'.format(self._planner_type))

        return mpc_policy

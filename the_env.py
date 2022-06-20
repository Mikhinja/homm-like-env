from datetime import datetime
from itertools import count
from HOMMGymEnv import HOMMGymEnv
#from stable_baselines3 import DQN, PPO
#from stable_baselines3.common.evaluation import evaluate_policy

import gym, ray
from ray.rllib.agents import ppo

from time import time
from HOMM.HOMMActions import ActionEndTurn

from HOMM.HOMMBuiltInAI_Battle import BattleAction
from random import randint

from ray import tune
from ray.tune.registry import register_env

allowed_actions_per_turn=30
max_day = '1:3:2'
def env_creator(env_config):
    start_start = time()

    # set this to some number to fix the map, None for randomly generated maps
    fixed_seed = None # None # randint(0, 1<<32)
    # map sizes: T=19x19, S-=27x27, S=36x36, S+=36x56, M=72x72, L=108x108, XL= 144x144, H=180x180, XH=216x216, G=252x252
    map_size = 'T'

    extra_desc = 'minimal vsDummyAI'

    env = HOMMGymEnv(map_size=map_size,
        max_day=max_day,
        allowed_actions_per_turn=allowed_actions_per_turn,
        p2_use_procedural_ai=True, p2_dummy_num=0,
        #observation_encoding='dict', action_mapper='big-flat'
        #observation_encoding='selection-flat', action_mapper='selection',
        # observation_encoding='selection-flat', action_mapper='selection-reduced',
        # observation_encoding='minimal', action_mapper='minimal',
        # observation_encoding='minimal', action_mapper='only-move',
        observation_encoding='really-minimal-flat', action_mapper='only-move',
        fixed_seed=fixed_seed
    )
    return env

register_env('homm_env_tiny_trivial', env_creator=env_creator)

# ray.init()

# # trainer = ppo.PPOTrainer(env='homm_env_tiny_trivial')
# # trainer.train()

# analysis = tune.run(
#     "DQN",
#     stop={"episode_reward_mean":500, "training_iteration":100_000},
#     config={
#         "env": "homm_env_tiny_trivial",
#         "num_workers": 16,
#         "kl_coeff": 1.0, # this is default, not sure if it should be reduced?
#         "lambda": 0.95,
#         "clip_param": 0.2,
#         "lr": tune.grid_search([0.1, 0.01, 0.001]),
#         "num_sgd_iter": tune.choice([10, 20, 30]),
#         "sgd_minibatch_size": tune.choice([128, 512, 2048]),
#         "train_batch_size": tune.choice([10000, 20000, 40000]),
#     }
# )

# print("best hyperparameters: ", analysis.best_config)

import numpy as np
import torch
import torch.optim as optim
import torch.nn as nn
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import torch.nn.functional as F

from ray import tune
#from ray.tune.schedulers import ASHAScheduler
from ray.cluster_utils import AutoscalingCluster
import ray
from HOMM.HOMMAPI import HOMMMap

import the_env

import seaborn as sns
sns.set()

ray.init()

# trainer = ppo.PPOTrainer(env='homm_env_tiny_trivial')
# trainer.train()

cluster = AutoscalingCluster(
    head_resources={"CPU": 2},
    worker_node_types={
        "cpu_node": {
            "resources": {
                "CPU": 16,
                "object_store_memory": 30 * 1024 * 1024 * 1024, # 30 GB?
            },
            "node_config": {},
            "min_workers": 0,
            "max_workers": 2,
        },
        "gpu_node": {
            "resources": {
                "CPU": 16,
                "GPU": 1,
                "object_store_memory": 2 * 1024 * 1024 * 1024, # 2 GB?
            },
            "node_config": {},
            "min_workers": 0,
            "max_workers": 16,
        },
    },
)

try:
    # cluster.start()
    # ray.init("auto")

    # # Triggers the addition of a GPU node.
    # @ray.remote(num_gpus=1)
    # def f():
    #     print("gpu ok")
    
    # # Triggers the addition of a CPU node.
    # @ray.remote(num_cpus=3)
    # def g():
    #     print("cpu ok")
    
    # ray.get(f.remote())
    # ray.get(g.remote())

    from ray.tune.utils.log import Verbosity

    analysis = tune.run(
        "PPO", # ?
        # "DQN",
        #"R2D2",
        #"APEX", #  APEX or APEX_DDPG ? Sadly my main machine doesn't have NVIDIA compatible GPU :`(

        resume=True,

        # metric='episode_reward_mean', # is this ok?
        # mode='max',
        #checkpoint_freq=5,
        verbose=Verbosity.V3_TRIAL_DETAILS,

        stop={"training_iteration":500, "timesteps_total":100_000}, # "episode_reward_mean":30, this sounds like a bad idea
        config={
            "env": "homm_env_tiny_trivial",
            "horizon": (the_env.allowed_actions_per_turn*HOMMMap.DayFromStr(the_env.max_day)), # is this ok? what's soft_horizon?
            # "zero_init_states": False, # for R2D2
            # "model": { # this is required for R2D2, but not for DQN?
            #     "use_lstm": True # alternatively use_attention
            # },

            #"double_q": False, # for DQN -- does this fix the double vs float issue?

            "num_workers": 16,
            "framework": "tf2",
            #"simple_optimizer": True,
            "eager_tracing": False, # is this ok?

            # "replay_buffer_config": {
            #     "capacity": 50_000,
            #     "prioritized_replay_alpha": 0.6,
            #     "prioritized_replay_beta": 0.4, # Beta parameter for sampling from prioritized replay buffer.
            #     "prioritized_replay_eps": 1e-6, # Epsilon to add to the TD errors when updating priorities.
            #     #"replay_sequence_length": 1, # The number of continuous environment steps to replay at once. Should this be the same as the env's max actions per turn?
            # },
            # "sigma0": 0.5,
            # #"n_step": 50,
            "lr": tune.grid_search([0.001, 0.0008]),
            "gamma": 0.99, # is this discount factor better than their default?

            ### for PPO
            "kl_coeff": 1.0, # this is default, not sure if it should be reduced?
            #"lambda": 0.95,
            #"clip_param": 0.2,
            #"num_sgd_iter": tune.choice([10, 20, 30]),
            "sgd_minibatch_size": tune.grid_search([128, 256, 300]),
            
            ## for DQN and R2D2 - not for PPO?
            # "train_batch_size": tune.grid_search([
            #     #6*the_env.allowed_actions_per_turn,
            #     8*the_env.allowed_actions_per_turn,
            #     10*the_env.allowed_actions_per_turn,
            #     12*the_env.allowed_actions_per_turn,
            #     #the_env.allowed_actions_per_turn*HOMMMap.DayFromStr(the_env.max_day), # this should be reduced a bit, it performs slightly worse than 8*allowed_actions_per_turn
            #     # 10_000,
            #     # 20_000,
            #     # 40_000
            # ]),
        }
    )

    # print("best hyperparameters: ", analysis.best_config)
    print("best hyperparameters (explicit): ", analysis.get_best_config(metric='episode_reward_mean', scope='last-10-avg', mode='max'))
    

    # ray.shutdown()

finally:
    pass
    # cluster.shutdown()

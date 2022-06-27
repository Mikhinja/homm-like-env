#import gym # is this needed?
from datetime import datetime
from itertools import count
import HOMMGymEnv
from stable_baselines3 import DQN, PPO

from stable_baselines3.common.evaluation import evaluate_policy

from time import time
from HOMM.HOMMActions import ActionEndTurn

from HOMM.HOMMBuiltInAI_Battle import BattleAction
from random import randint

allowed_actions_per_turn=20
start_start = time()

# set this to some number to fix the map, None for randomly generated maps
fixed_seed = randint(0, 1<<32) # None # randint(0, 1<<32)

# map sizes: T=19x19, S-=27x27, S=36x36, S+=36x56, M=72x72, L=108x108, XL= 144x144, H=180x180, XH=216x216, G=252x252
map_size = 'T'
max_day = '1:3:2'

env = HOMMGymEnv.HOMMGymEnv(map_size=map_size,
    max_day=max_day,
    allowed_actions_per_turn=allowed_actions_per_turn,
    p2_use_procedural_ai=True, p2_dummy_num=0,
    #observation_encoding='dict', action_mapper='big-flat'
    #observation_encoding='selection-flat', action_mapper='selection',
    # observation_encoding='selection-flat', action_mapper='selection-reduced',
    # observation_encoding='minimal', action_mapper='minimal',
    # observation_encoding='minimal', action_mapper='only-move',
    observation_encoding='really-minimal-flat', action_mapper='minimal',
    fixed_seed=fixed_seed
)

extra_desc = f'minimal-ish v DummyAI{env.p2_dummy_num}'

# MlpPolicy -- does not support dict as observation space
# model = PPO('MultiInputPolicy', env, verbose=1)
learning_rate = 8e-4 # good results between 8e-4 and 1e-3
buffer_size = 100_000 # de facut mai mare (mult mai mare decat 700)!
exploration_fraction = 0.4

# TODO: redus spatiul actiunilor ~15

### MultiInputPolicy  MlpPolicy
# model = PPO('MlpPolicy', env=env, verbose=1,
#     learning_rate=learning_rate,
#     batch_size=120, # 240?
#     n_steps=10*120, # make this bigger, a multiple of batch_size
#     gamma=0.99,
#     #n_epochs=env.game.max_day, # is this ok, to have an entire game?
    
# )

### MultiInputPolicy  MlpPolicy
model = DQN('MlpPolicy', env, verbose=1,
    buffer_size=buffer_size,
    learning_rate=learning_rate,
    #tau=0.9,
    gamma=0.99,
    learning_starts=10_000,
    exploration_fraction=exploration_fraction,
    #exploration_final_eps=0.1,
    #train_freq=(allowed_actions_per_turn//10, 'step')
    train_freq=(50, 'step'), # 50 - 100 # 'step' or 'episode'
    batch_size=300 # also good results with 240
)

total_timesteps=int(200_000)
print(f'{type(model)}\n  {extra_desc}'
f' training total_timesteps={total_timesteps}, learning-rate={learning_rate}'
f' map-size_{map_size}_{env.game.map.size[0]}x{env.game.map.size[1]}, fixed_seed={fixed_seed},'
f' turn-max_{allowed_actions_per_turn}, day-max_{env.game.max_day}...')

start = time()
try:
    model.learn(total_timesteps=total_timesteps,
    log_interval=16)
except KeyboardInterrupt:
    print(f'interupted after {env.TRAIN_STEP}')
except Exception as ex:
    if env:
        with open('env_dumps\\env_dump.json', 'w') as f:
            f.write(env.game.SaveState())
    raise
curr_time = time()-start

print(f'training done in {curr_time:> 5.2f}s. exploration_fraction={exploration_fraction}')

time_stamp = str(datetime.today())
time_stamp = time_stamp[:time_stamp.index('.')].replace(':', '.')
saved_name = (f'{model.__class__.__name__} map={env.game.map.size[0]}x{env.game.map.size[1]} seed={fixed_seed}'
f' maxAct={allowed_actions_per_turn} maxDay={env.game.max_day} steps={env.TRAIN_STEP:.0e}'
f' lr={learning_rate:.0e} batch={model.batch_size} exFr={model.exploration_fraction}'
f' {extra_desc} trT={int(curr_time//3600)}h.{int((curr_time % 3600)//60)}m at {time_stamp}.zip')
print(f'saving model "{saved_name}" ...')
model.save('trained_models\\'+saved_name)


print(f'actions that won: {", ".join([str(a) for a in HOMMGymEnv.HOMMGymEnv.ACTIONS_THAT_WON])}')


if fixed_seed:
    env_dump_file = f'env_dumps\\env_seed={fixed_seed}_dump.json'
    with open(env_dump_file, 'w') as f:
            f.write(env.game.SaveState())
    print(f'\nsaved env as {env_dump_file}')

with open(f'train_action_logs\\action_rewards_seed={fixed_seed}.txt', 'w') as f:
    print(f'{model.__class__.__name__}, fix-seed={fixed_seed} {extra_desc}, L-rate_{learning_rate}', file=f)
    print(f'train time={int(curr_time//3600)}h.{int((curr_time % 3600)//60)}m, at {time_stamp}', file=f)
    print(f'saved as {saved_name}', file=f)
    for a in HOMMGymEnv.HOMMGymEnv.ACTION_REWARDS:
        print(str(a), file=f)

#del model
#print(f'loading model {saved_name}...')
#model = DQN.load(saved_name, env=env)

#input('traing done, press any key...')

# n_eval_episodes=1
# print(f'evaluating n_eval_episodes={n_eval_episodes}...')
# start = time()
# mean_reward, std_reward = evaluate_policy(model, model.get_env(), n_eval_episodes=n_eval_episodes)
# curr_time = time()-start
# print(f'evaluated on {n_eval_episodes} episodes in {curr_time:> 5.2f}s, mean_reward={mean_reward}, std_reward={std_reward}')

#input('evaluating done, press any key...')

play_a_game = False
if play_a_game:
    # the +1 is there because there can also be unacceptable actions which are not counted
    #   ...they could go on forever, but without them the game could end up in an invalid state
    max_steps = max(1500, (env.game.max_day+1)*allowed_actions_per_turn)
    print(f'playing a game (at most {max_steps} steps)')
    obs = env.reset()
    start = time()
    for i in range(max_steps):
        action, _states = model.predict(obs, deterministic=True)
        obs, rewards, dones, info = env.step(action=action)
        if env.game.ended:
            break
    curr_time = time()-start
    print(f'after {i} steps played in {curr_time:> 5.2f}s: game.ended={env.game.ended}, day={env.game.map.GetDayStr()}'
        f'\n\t total-actions={len(env.game.actions_log.actions)}, P1-total-actions={len([a for a in env.game.actions_log.actions if a.player_idx==env.ML_player_idx])}'
        f'\n\t num-invalid-actions={len([a for a in env.game.actions_log.actions if a.player_idx==env.ML_player_idx and not a.is_valid])},'
        f'\n\t num-valid-actions-not-forced={len([a for a in env.game.actions_log.actions if a.player_idx==env.ML_player_idx and a.is_valid and not a.is_forced and type(a) != BattleAction])}'
        f'\n\t won={env.ML_player_idx in env.game.winners}, defeated={env.game.map.players[env.ML_player_idx].IsDefeated()}'
        f', end-AIVal={env.game.map.players[env.ML_player_idx].GetAIVal()}')

    num_valid_actions_from_agent = 0
    for idx, a in enumerate(env.game.actions_log.actions):
        if a.player_idx == env.ML_player_idx and a.is_valid and type(a) != BattleAction:
            print(f'[{idx:> 5}] day={a.day:> 2} action: {str(a)}')
            if not a.is_forced:
                num_valid_actions_from_agent += 1

curr_time = time()-start_start
print(f'(total time so far {curr_time:> 5.3f}s)')

# for profiling:  python -m cProfile -o train_test.stats train.py
# to investigate: python -m pstats train_test.stats

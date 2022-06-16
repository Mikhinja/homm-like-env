from datetime import datetime
from itertools import count
import HOMMGymEnv
from stable_baselines3 import DQN, PPO

from stable_baselines3.common.evaluation import evaluate_policy

from time import time

from HOMM.HOMMBuiltInAI_Battle import BattleAction
from HOMM.HOMMRenderer import HOMMColorTextConsoleRender, cls
import sys

cls()

max_day = '1:3:2'

allowed_actions_per_turn=50
env = HOMMGymEnv.HOMMGymEnv(map_size='S-', max_day=max_day,
    allowed_actions_per_turn=allowed_actions_per_turn,
    p2_use_procedural_ai=True, p2_dummy_num=0,
    #observation_encoding='dict', action_mapper='big-flat'
    #observation_encoding='selection-flat', action_mapper='selection',
    # observation_encoding='minimal', action_mapper='minimal',
    observation_encoding='really-minimal', action_mapper='only-move',
    fixed_seed=202602822,
)

#'PPO turnmax_50 timesteps_50000 at 2022-06-10 23.44.53'
#'DQN turnmax_50 timesteps_10000 at 2022-06-11 16.50.56'
#'PPO turnmax_50 timesteps_30000 at 2022-06-11 19.11.33.zip'
# 'DQN map-size_S-_27x27 turn-max_40 day-max_15 T-steps_20000 L-rate_0.5 fix-seed_3103147081 vsDummyAI trainT_1h.9m at 2022-06-13 16.21.38.zip'
# 'DQN map-size_S-_27x27 turn-max_40 day-max_15 T-steps_20000 L-rate_0.2 fix-seed_849698169 vsDummyAI trainT_1h.2m at 2022-06-13 17.41.36.zip'
# 'DQN map-size_S-_27x27 turn-max_40 day-max_15 T-steps_5000 L-rate_0.2 fix-seed_1220620616 vsDummyAI trainT_0h.15m at 2022-06-13 19.59.59.zip'
# 'DQN map-size_S-_27x27 turn-max_40 day-max_15 T-steps_10000 L-rate_0.1 fix-seed_1667361835 vsDummyAI trainT_0h.30m at 2022-06-14 14.25.51.zip'
# 'DQN map-size_S-_27x27 turn-max_40 day-max_15 T-steps_80000 L-rate_0.2 fix-seed_3283905031 vsDummyAI trainT_0h.55m at 2022-06-14 18.43.04.zip'
# 'PPO map-size=27x27 turn-max_40 day-max=15 T-steps=30000 L-rate=0.2 fix-seed=474806171 minimal_vsDummyAI trainT=0h.52m at 2022-06-15 15.01.07.zip'
saved_name = 'DQN map-size=27x27 turn-max_30 day-max=15 T-steps=100000 L-rate=0.05 fix-seed=202602822 minimal_vsDummyAI trainT=0h.7m at 2022-06-16 17.50.49.zip'
print(f'loading model "{saved_name}" ...')
model = DQN.load('trained_models\\'+saved_name, env=env)
# model = DQN.load('trained_models\\'+saved_name, env=env)

# the +1 is there because there can also be unacceptable actions which are not counted
#   ...they could go on forever, but without them the game could end up in an invalid state
max_steps = max(1500, (env.game.max_day+1)*allowed_actions_per_turn)
print(f'playing a game (at most {max_steps} steps)')
start = time()

obs = env.reset()
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
    f', end-AIVals=[{env.game.map.players[0].GetAIVal()}, {env.game.map.players[1].GetAIVal()}]'
    f'\n\t end reward={env.total_rewards[0]}\n')

# print('relevant actions:')
# for idx, a in enumerate(env.game.actions_log.actions):
#     if a.player_idx == env.ML_player_idx and a.is_valid and type(a) != BattleAction and not a.is_forced:
#         print(f'[{idx:> 5}] day={a.day:> 2} action: {str(a)}')

print('rendering...\n')

env.game.SetRenderer('colortext')
renderer:HOMMColorTextConsoleRender = env.game.renderer
renderer.print_battles = False
renderer.__init_console_render__()
snapshot = renderer.__print_all__()
snapshot = renderer.__print_map__() + '\n' + snapshot

sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (31, 1, snapshot))
sys.stdout.flush()

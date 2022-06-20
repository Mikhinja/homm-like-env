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
env = HOMMGymEnv.HOMMGymEnv(map_size='T', max_day=max_day,
    allowed_actions_per_turn=allowed_actions_per_turn,
    p2_use_procedural_ai=True, p2_dummy_num=0,
    #observation_encoding='dict', action_mapper='big-flat'
    #observation_encoding='selection-flat', action_mapper='selection',
    # observation_encoding='minimal', action_mapper='minimal',
    # observation_encoding='really-minimal-flat', action_mapper='only-move',
    observation_encoding='really-minimal-flat', action_mapper='minimal',
    fixed_seed=None,
)

#'DQN map=19x19 turn-max_30 day-max=15 steps=200000 L-rate=0.001 seed=44793690 minimal-ish_vsDummyAI trainT=0h.21m at 2022-06-17 23.48.18.zip'
# 'DQN map=19x19 turn-max_30 day-max=15 steps=200000 L-rate=0.001 seed=1024681898 minimal-ish_vsDummyAI trainT=0h.23m at 2022-06-18 00.25.37.zip'
saved_name = 'DQN map=19x19 turn-max_30 day-max=15 steps=200000 L-rate=0.001 seed=None minimal-ish_vsDummyAI trainT=0h.21m at 2022-06-18 00.58.01.zip'
print(f'loading model "{saved_name}" ...')
model = DQN.load('trained_models\\'+saved_name, env=env)
# model = DQN.load('trained_models\\'+saved_name, env=env)

# the +1 is there because there can also be unacceptable actions which are not counted
#   ...they could go on forever, but without them the game could end up in an invalid state
max_steps = max(1500, (env.game.max_day+1)*allowed_actions_per_turn)
print(f'playing a game (at most {max_steps} steps)')
start = time()

obs = env.reset()
env.game.SetRenderer('colortext')
renderer:HOMMColorTextConsoleRender = env.game.renderer
renderer.print_battles = False
renderer.interactive_play = True
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

# print('rendering...\n')
input('press any key, to render...')
if renderer:
    renderer.__init_image_capture__()
    renderer.Playback()

# env.game.SetRenderer('colortext')
# renderer:HOMMColorTextConsoleRender = env.game.renderer
# renderer.print_battles = False
# renderer.__init_console_render__()
# snapshot = renderer.__print_all__()
# snapshot = renderer.__print_map__() + '\n' + snapshot

# sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (31, 1, snapshot))
# sys.stdout.flush()

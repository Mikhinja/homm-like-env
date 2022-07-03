from copy import copy, deepcopy
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

# max_day = '1:2:7'
max_day = '1:3:2'

allowed_actions_per_turn=10
env = HOMMGymEnv.HOMMGymEnv(map_size='T', max_day=max_day,
    allowed_actions_per_turn=allowed_actions_per_turn,
    
    p2_use_procedural_ai=True, #p2_dummy_num=2,
    #p2_use_procedural_ai=False,

    #observation_encoding='dict', action_mapper='big-flat'
    #observation_encoding='selection-flat', action_mapper='selection',
    # observation_encoding='minimal', action_mapper='minimal',
    # observation_encoding='really-minimal-flat', action_mapper='only-move',
    observation_encoding='really-minimal-flat', action_mapper='minimal',
    fixed_seed=656093448,
)

### latest
# 'DQN map=19x19 seed=3128162577 maxAct=20 maxDay=15 steps=2e+05 lr=8e-04 batch=300 exFr=0.4 minimal-ish v DummyAI0 trT=0h.16m at 2022-06-27 22.21.29.zip'
# 'DQN map=19x19 seed=None maxAct=20 maxDay=15 steps=3e+05 lr=8e-04 batch=300 exFr=0.4 minimal-ish v DummyAI0 trT=0h.20m at 2022-06-29 00.32.09.zip'
# 'DQN map=19x19 seed=None maxAct=20 maxDay=15 steps=2e+05 lr=8e-04 batch=300 exFr=0.4 minimal-ish v ProceduralAI-1 trT=0h.22m at 2022-07-03 14.03.46.zip' # still negative
# 'DQN map=19x19 seed=2123588468 maxAct=10 maxDay=15 steps=3e+05 lr=8e-04 batch=300 exFr=0.4 minimal-ish v ProceduralAI-1 trT=0h.36m at 2022-07-03 15.51.21.zip' # doesn't lose outright

# 'PPO map=19x19 seed=4161212843 maxAct=20 maxDay=15 steps=2e+05 lr=8e-04 batch=120  minimal-ish v DummyAI0 trT=0h.20m at 2022-06-28 23.55.34.zip'
# 'PPO map=19x19 seed=None maxAct=20 maxDay=15 steps=2e+05 lr=8e-04 batch=120  minimal-ish v DummyAI0 trT=0h.24m at 2022-07-03 12.33.38.zip' # rw mean negative few tens
# 'PPO map=19x19 seed=None maxAct=20 maxDay=15 steps=2e+05 lr=8e-04 batch=120  minimal-ish v ProceduralAI-1 trT=0h.50m at 2022-07-03 13.33.32.zip' rw mean still negative
# 'PPO map=19x19 seed=656093448 maxAct=10 maxDay=15 steps=3e+05 lr=8e-04 batch=120  minimal-ish v ProceduralAI-1 trT=0h.31m at 2022-07-03 17.40.29.zip'

saved_name = 'PPO map=19x19 seed=656093448 maxAct=10 maxDay=15 steps=3e+05 lr=8e-04 batch=120  minimal-ish v ProceduralAI-1 trT=0h.31m at 2022-07-03 17.40.29.zip'
print(f'loading model "{saved_name}" ...')
# model = DQN.load('trained_models\\'+saved_name, env=env)
model = PPO.load('trained_models\\'+saved_name, env=env)

# for player 2
model2 = copy(model) # should this be deep? 

# the +1 is there because there can also be unacceptable actions which are not counted
#   ...they could go on forever, but without them the game could end up in an invalid state
max_steps = max(1500, (env.game.max_day+1)*allowed_actions_per_turn)
print(f'playing a game (at most {max_steps} steps)')
start = time()

obs = env.reset()
env.game.SetRenderer('colortext')
renderer:HOMMColorTextConsoleRender = env.game.renderer
renderer.print_battles = True
renderer.interactive_play = True
for i in range(max_steps):
    if env.game.map.curr_player_idx == 0:
        action, _states = model.predict(obs, deterministic=True)
    else:
        action, _states = model2.predict(obs, deterministic=True)
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
input('press any key to render the game...')
if renderer:
    renderer.print_battles = False # this is to speed things up a bit
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

from HOMMGymEnv import HOMMGymEnv
from HOMM.HOMMEnv import HOMMSimpleEnv
from HOMM.HOMMRenderer import HOMMColorTextConsoleRender, cls
import sys

cls()

env = HOMMSimpleEnv()
# file_name = 'env_dump.json'
file_name = 'env_seed=3231024768_dump.json'
with open(f'env_dumps\\{file_name}', 'r') as f:
    s = f.read()
    env.LoadState(s)
    print('load done')

map_size = 'S-'
max_day = '1:3:2'
gymEnv = HOMMGymEnv(map_size=map_size,
    max_day=max_day,
    allowed_actions_per_turn=40,
    p2_use_procedural_ai=True, p2_dummy_num=0,
    #observation_encoding='dict', action_mapper='big-flat'
    #observation_encoding='selection-flat', action_mapper='selection',
    observation_encoding='minimal', action_mapper='minimal')

gymEnv.game = env
obs = gymEnv.observer.GetObservation(gymEnv)

env.SetRenderer('colortext')
renderer:HOMMColorTextConsoleRender = env.renderer
renderer.__init_console_render__()
snapshot = renderer.__print_all__()

sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (1, 1, snapshot))
sys.stdout.flush()



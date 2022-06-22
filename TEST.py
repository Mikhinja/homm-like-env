import itertools
import random
import sys

from time import sleep, time
import os

import jsonpickle
from HOMM.HOMMBuiltInAI_Procedural import ProceduralAI

from HOMM.HOMMEnv import HOMMSimpleEnv
from HOMM.HOMMMap import HardcodedTemplate

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

# from numpy import tile
from HOMM.HOMMAPI import HOMMAction, HOMMHero, HOMMMap
from HOMM.HOMMData.HOMMMapData import MapObjTypeById, MapObjectTypes, MapResPileToIdx, MapResPileTypicalValues, TileTypes
from HOMM.HOMMUnitTypes import UnitUtils
from HOMM.HOMMHeroes import HeroUtils, HeroSpellUtils, HeroSpells
from HOMM.HOMMUtils import pprint_army, pprint_2d, pprint_map
from HOMM.Battlefield import Battlefield
from HOMM.Battle import BattleFactory
from HOMM.Town import CastleTown
from HOMM.Hero import Hero

def add_resource_pile(the_map:HOMMMap, res_type:str, val_avg:int, exact:bool=False) -> tuple:
    if the_map:
        val = val_avg if exact else random.randrange(int(val_avg * 0.8), int(val_avg * 1.2))
        pos = random.randrange(0, the_map.size[0]), random.randrange(0, the_map.size[1])
        the_map.AddResource(*pos, MapObjectTypes[res_type]['id'], val)
        return pos
    return False
def add_gold_pile(the_map:HOMMMap, val_avg:int=500) -> tuple:
    if the_map:
        val = random.randrange(int(val_avg * 0.8), int(val_avg * 1.2))
        pos = random.randrange(0, the_map.size[0]), random.randrange(0, the_map.size[1])
        the_map.AddResource(*pos, MapObjectTypes['Gold pile']['id'], val)
        return pos
    return False
def add_wood_pile(the_map:HOMMMap, val_avg:int=8) -> tuple:
    if the_map:
        val = random.randrange(int(val_avg * 0.8), int(val_avg * 1.2))
        pos = random.randrange(0, the_map.size[0]), random.randrange(0, the_map.size[1])
        the_map.AddResource(*pos, MapObjectTypes['Wood pile']['id'], val)
        return pos
    return False
def add_ore_pile(the_map:HOMMMap, val_avg:int=8) -> tuple:
    if the_map:
        val = random.randrange(int(val_avg * 0.8), int(val_avg * 1.2))
        pos = random.randrange(0, the_map.size[0]), random.randrange(0, the_map.size[1])
        the_map.AddResource(*pos, MapObjectTypes['Ore pile']['id'], val)
        return pos
    return False
def add_random_resource_pile(the_map:HOMMMap) -> tuple:
    if the_map:
        res_type_id = random.choice([res_id for res_id in MapResPileToIdx])
        res_type = MapObjTypeById[res_type_id]
        res_val = MapResPileTypicalValues[res_type_id]
        return add_resource_pile(the_map, res_type, res_val)
    return False

def TEST_2_2P_build_in_AI(render:bool=True, replay:bool=False) -> HOMMSimpleEnv:
    if render:
        env = HOMMSimpleEnv(renderer='colortext', num_players=2, max_day='1:2:7', map_size=(36, 42))
        # debug battles options
        # env.renderer.frame_delay=0.1
        # env.renderer.frame_delay_battle=0.1
        # env.renderer.num_actions=1
        # env.renderer.record_animation=True
        # env.renderer.animation_frame_delay=0.5
    else:
        env = HOMMSimpleEnv(num_players=2, max_day='1:2:7')
    env.check_same_action_in_succession = True

    ProceduralAI(env, env.map.players[0])
    ProceduralAI(env, env.map.players[1])

    town = CastleTown(3,3, rng=env.rs)
    env.map.AddTown(town)
    town.Build('Guardhouse')
    town.built_today = False
    town.Build('Archer\'s Tower')
    town.built_today = False
    env.map.players[0].TakeTown(town)
    town = CastleTown(21,21, rng=env.rs)
    env.map.AddTown(town)
    town.Build('Guardhouse')
    town.built_today = False
    town.Build('Archer\'s Tower')
    town.built_today = False
    env.map.players[1].TakeTown(town)

    env.map.GiveHeroTo(env.map.heroes[0], env.map.players[0], ( 3,  3))
    env.map.GiveHeroTo(env.map.heroes[1], env.map.players[1], (21, 21))

    env.map.players[0].heroes[0].LearnSpell(HeroSpellUtils.GetSpellId('shield'))
    env.map.players[0].heroes[0].LearnSpell(HeroSpellUtils.GetSpellId('magic arrow'))
    env.map.players[0].heroes[0].LearnSpell(HeroSpellUtils.GetSpellId('haste'))

    env.map.players[1].heroes[0].LearnSpell(HeroSpellUtils.GetSpellId('curse'))
    env.map.players[1].heroes[0].LearnSpell(HeroSpellUtils.GetSpellId('magic arrow'))
    env.map.players[1].heroes[0].LearnSpell(HeroSpellUtils.GetSpellId('slow'))

    for _ in range(2):
        add_gold_pile(env.map)
        add_wood_pile(env.map)
        add_ore_pile(env.map)
        add_random_resource_pile(env.map)
        add_random_resource_pile(env.map)
        add_random_resource_pile(env.map)
        add_resource_pile(env.map, 'Treasure Chest', random.choice([500, 1000, 1500]), exact=True)
        add_resource_pile(env.map, 'Treasure Chest', random.choice([500, 1000, 1500]), exact=True)
        add_resource_pile(env.map, 'Treasure Chest', random.choice([500, 1000, 1500]), exact=True)
    
    if replay:
        env.interrupt_daily = True
        # env.interrupt_after_each_action = True
        env_start_state = env.SaveState()
        # env.LoadState(env_start_state)
        env2 = HOMMSimpleEnv()
        env2.LoadState(env_start_state)
        assert str(env.rng_start_state) == str(env2.rng_start_state), 'RNG start states differ!'
        env.Start()
        env2.Start()
        assert str(env.rs.get_state()) == str(env2.rs.get_state()), 'RNG states differ!'

        redone_once = False
        while not env.ended and not env2.ended:
            try:
                assert env.ended == env2.ended, 'env.ended'
                assert env.map.day == env2.map.day, 'env.map.day'
                if len(env.actions_log.actions) != len(env2.actions_log.actions):
                    idx = next(idx for idx in range(min(len(env.actions_log.actions), len(env2.actions_log.actions)))
                        if jsonpickle.encode(env.actions_log.actions[idx]) != jsonpickle.encode(env2.actions_log.actions[idx]))
                assert len(env.actions_log.actions) == len(env2.actions_log.actions), f'len(env.actions_log.actions) differs first at {idx}'
                for idx in range(len(env.actions_log.actions)):
                    a1 = env.actions_log.actions[idx]
                    a2 = env2.actions_log.actions[idx]
                    assert type(a1) == type(a2), f'type {type(a1)} == {type(a2)}'
                    assert a1.result == a2.result, f'result {a1.result} == {a2.result}'
                    assert a1.result_what == a2.result_what, f'result_what {a1.result_what} == {a2.result_what}'
                    assert a1.result_where == a2.result_where, f'result_where {a1.result_where} == {a2.result_where}'
                    assert a1.is_valid == a2.is_valid, 'is_valid'
                    assert jsonpickle.encode(a1) == jsonpickle.encode(a2), 'jsonpickle'
                assert str(env.rs.get_state()) == str(env2.rs.get_state()), 'RNG states differ!'
                assert env.curr_day_state == env2.curr_day_state, f'difference before day {env.map.day}'
            except AssertionError as err:
                if not redone_once:
                    env.LoadState(env.prev_day_state)
                    env2.LoadState(env2.prev_day_state)
                    redone_once = True
                else:
                    redone_once = False
            env.ContinueAuto()
            env2.ContinueAuto()
    else:
        env.Start()
    
    if env.renderer:
        env.renderer.__init_image_capture__()
        env.renderer.Playback()
    
    return env


def TEST_Hardcoded_Template_Env(render:bool=True, replay:bool=False, use_map_cache:bool=False, only_generate:bool=False, seed:int=None) -> HOMMSimpleEnv:
    template = HardcodedTemplate(areas=4, size='S+', max_day='1:3:7')
    env = template.Generate(seed=seed)
    if only_generate:
        return env
    if render:
        env.SetRenderer(renderer='colortext')
    env.check_same_action_in_succession = True
    env.map._cache_astar = use_map_cache
    
    ProceduralAI(env, env.map.players[0])
    ProceduralAI(env, env.map.players[1])

    if replay:
        env.interrupt_daily = True
        # env.interrupt_after_each_action = True
        env_start_state = env.SaveState()
        # env.LoadState(env_start_state)
        env2 = HOMMSimpleEnv()
        env2.LoadState(env_start_state)
        assert str(env.rng_start_state) == str(env2.rng_start_state), 'RNG start states differ!'
        env.Start()
        env2.Start()
        assert str(env.rs.get_state()) == str(env2.rs.get_state()), 'RNG states differ!'

        redone_once = False
        while not env.ended and not env2.ended:
            try:
                assert env.ended == env2.ended, 'env.ended'
                assert env.map.day == env2.map.day, 'env.map.day'
                if len(env.actions_log.actions) != len(env2.actions_log.actions):
                    idx = next(idx for idx in range(min(len(env.actions_log.actions), len(env2.actions_log.actions)))
                        if jsonpickle.encode(env.actions_log.actions[idx]) != jsonpickle.encode(env2.actions_log.actions[idx]))
                assert len(env.actions_log.actions) == len(env2.actions_log.actions), f'len(env.actions_log.actions) differs first at {idx}'
                for idx in range(len(env.actions_log.actions)):
                    a1 = env.actions_log.actions[idx]
                    a2 = env2.actions_log.actions[idx]
                    assert jsonpickle.encode(a1) == jsonpickle.encode(a2), 'jsonpickle'
                assert str(env.rs.get_state()) == str(env2.rs.get_state()), 'RNG states differ!'
                assert env.curr_day_state == env2.curr_day_state, f'difference before day {env.map.day}'
            except AssertionError as err:
                if not redone_once:
                    env.LoadState(env.prev_day_state)
                    env2.LoadState(env2.prev_day_state)
                    redone_once = True
                else:
                    redone_once = False
            env.ContinueAuto()
            env2.ContinueAuto()
    else:
        env.Start()

    if env.renderer:
        env.renderer.__init_image_capture__()
        env.renderer.Playback()
    
    return env



#input('press any key')
import win32gui, win32process, psutil

def active_window_process_name():
    try:
        pid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())
        return(psutil.Process(pid[-1]).name())
    except Exception as e:
        pass

curr_proc_name = active_window_process_name()
run_in_cmd = 'cmd.exe' in curr_proc_name.lower()

num_games = 0

if num_games:
    seeds = [random.randint(0, 2**31) for _ in range(num_games)]

    sum_time = 0
    sum_actions = 0
    sum_invalid_actions = 0
    replay = True
    print(f'replay={replay} ({"run twice and compare" if replay else "run just once"})')

    start = time()
    env = TEST_2_2P_build_in_AI(render=False, replay=replay)
    curr_time = time()-start
    sum_time += curr_time
    sum_actions += len(env.actions_log.actions)
    invalid_actions = sum(1 for a in env.actions_log.actions if not a.is_valid)
    sum_invalid_actions += invalid_actions
    print(f' test  0 done in: {curr_time:>2.3f} sec, day: {env.map.GetDayStr()}, winners: {[p.idx+1 for p in env.winners]}, actions: {len(env.actions_log.actions):>5}, invalid actions: {invalid_actions:>3}.\n')

    sum_time = 0
    sum_actions = 0
    sum_invalid_actions = 0

    test_without_cache = True
    if test_without_cache:
        print(f'\n === no cache ===')
        for i in range(num_games):
            #print(f' === test {i+1:> 2} ===')
            start = time()
            # env = TEST_2_2P_build_in_AI(render=False, replay=replay)
            env1 = TEST_Hardcoded_Template_Env(render=False, replay=replay, seed=seeds[i])
            curr_time = time()-start
            sum_time += curr_time
            sum_actions += len(env1.actions_log.actions)
            invalid_actions = sum(1 for a in env1.actions_log.actions if not a.is_valid)
            sum_invalid_actions += invalid_actions
            print(f' test {i+1:>2} done in: {curr_time:>2.3f} sec, day: {env1.map.GetDayStr()}, winners: {[p.idx+1 for p in env1.winners]}, actions: {len(env1.actions_log.actions):>5}, invalid actions: {invalid_actions:>3}.')
        sleep(1)

        print(f"""Average (no cache):
        time/game = {(sum_time/(num_games)):>2.3f}, time/action = {(sum_time/sum_actions):>2.5f}
        actions/game = {(sum_actions/(num_games)):>6.2f}, invalid actions/game = {(sum_invalid_actions/(num_games)):>4.2f}""")

    sum_time = 0
    sum_actions = 0
    sum_invalid_actions = 0

    test_with_cache = True
    if test_with_cache:
        print(f'\n === with cache ===')
        for i in range(num_games):
            #print(f' === test {i+1:> 2} ===')
            start = time()
            # env = TEST_2_2P_build_in_AI(render=False, replay=replay)
            env2 = TEST_Hardcoded_Template_Env(render=False, replay=replay, seed=seeds[i], use_map_cache=True)
            curr_time = time()-start
            sum_time += curr_time
            sum_actions += len(env2.actions_log.actions)
            invalid_actions = sum(1 for a in env2.actions_log.actions if not a.is_valid)
            sum_invalid_actions += invalid_actions
            print(f' test {i+1:>2} done in: {curr_time:>2.3f} sec, day: {env2.map.GetDayStr()}, winners: {[p.idx+1 for p in env2.winners]}, actions: {len(env2.actions_log.actions):>5}, invalid actions: {invalid_actions:>3}.')
        sleep(1)

        print(f"""Average (with cache):
        time/game = {(sum_time/(num_games)):>2.3f}, time/action = {(sum_time/sum_actions):>2.5f}
        actions/game = {(sum_actions/(num_games)):>6.2f}, invalid actions/game = {(sum_invalid_actions/(num_games)):>4.2f}""")

#input('press any key')
run_in_cmd=True
if run_in_cmd:
    TEST_Hardcoded_Template_Env(render=run_in_cmd)

# print("\n === Starting generated game ===")
# env = TEST_Hardcoded_Template_Env(render=True, replay=False)

# To debug attached run: python -m debugpy --listen 5678 .\TEST.py


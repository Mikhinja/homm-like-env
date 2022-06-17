from typing import OrderedDict
from gym import Space, spaces
from numpy import int16, int8
from HOMMGymEnv import HOMMGymEnv, GameObserver, GameActionMapper
from HOMM.HOMMAPI import HOMMAction, HOMMArmy, HOMMArmyStack
from HOMM.HOMMActions import ActionBuild, ActionChangeSelection, ActionEndTurn, ActionMoveHero, ActionRecruitArmy, ActionRecruitHero, ActionSkillChoice, ActionTransferArmy
from HOMM.HOMMData.HOMMHeroData import HeroSkills, HeroSpells
from HOMM.HOMMData.HOMMMapData import TileTypesByName
from HOMM.HOMMData.HOMMTownData import TownTypes
from HOMM.HOMMData.HOMMUnitData import UnitTypes
from HOMM.Hero import Hero
from HOMM.Town import TownBase

from GymExtensions import DiscreteMasked
import numpy as np

class GameObserverSelectedHeroTown(GameObserver):
    def __init__(self) -> None:
        self._total_unit_types = len(UnitTypes)
        self.buildings_list = [b for b in TownTypes['Castle']['Buildings']]
        self.total_buildings_num = len(self.buildings_list)
        # self.sel_hero_idx = 1 # starting hero
        # self.sel_town_idx = 1 # starting town
        self.desc_dict = OrderedDict()
        self.obs_dict = OrderedDict()
        self.__last_active_player_idx = 0

    def __hero_desc__(self, env:HOMMGymEnv, idx:int, own:bool=True):
        key_base = f'{"own" if own else "enemy"}hero{idx+1}'
        self.desc_dict[key_base+'-x'] = spaces.Discrete(env.game.map.size[0])
        self.desc_dict[key_base+'-y'] = spaces.Discrete(env.game.map.size[1])
        self.desc_dict[key_base+'-attack'] = spaces.Discrete(99)
        self.desc_dict[key_base+'-defense'] = spaces.Discrete(99)
        self.desc_dict[key_base+'-power'] = spaces.Discrete(99)
        self.desc_dict[key_base+'-knowledge'] = spaces.Discrete(99)
        self.desc_dict[key_base+'-mana'] = spaces.Discrete(1000)
        self.desc_dict[key_base+'-movement'] = spaces.Discrete(4000)
        self.desc_dict[key_base+'-skills'] = spaces.Box(low=0, high=3, shape=(len(HeroSkills),), dtype=int16)
        self.desc_dict[key_base+'-spells'] = spaces.MultiBinary(len(HeroSpells))
        self.desc_dict[key_base+'-army1type'] = spaces.Discrete(self._total_unit_types)
        self.desc_dict[key_base+'-army1num'] =  spaces.Discrete(HOMMArmyStack.MAX_IN_STACK)
        self.desc_dict[key_base+'-army2type'] = spaces.Discrete(self._total_unit_types)
        self.desc_dict[key_base+'-army2num'] =  spaces.Discrete(HOMMArmyStack.MAX_IN_STACK)
        self.desc_dict[key_base+'-army3type'] = spaces.Discrete(self._total_unit_types)
        self.desc_dict[key_base+'-army3num'] =  spaces.Discrete(HOMMArmyStack.MAX_IN_STACK)
        self.desc_dict[key_base+'-army4type'] = spaces.Discrete(self._total_unit_types)
        self.desc_dict[key_base+'-army4num'] =  spaces.Discrete(HOMMArmyStack.MAX_IN_STACK)
        self.desc_dict[key_base+'-army5type'] = spaces.Discrete(self._total_unit_types)
        self.desc_dict[key_base+'-army5num'] =  spaces.Discrete(HOMMArmyStack.MAX_IN_STACK)
        self.desc_dict[key_base+'-army6type'] = spaces.Discrete(self._total_unit_types)
        self.desc_dict[key_base+'-army6num'] =  spaces.Discrete(HOMMArmyStack.MAX_IN_STACK)
        self.desc_dict[key_base+'-army7type'] = spaces.Discrete(self._total_unit_types)
        self.desc_dict[key_base+'-army7num'] =  spaces.Discrete(HOMMArmyStack.MAX_IN_STACK)
        
    def __town_desc__(self, env:HOMMGymEnv, idx:int, own:bool=True):
        key_base = f'{"own" if own else "other"}town{idx+1}'
        self.desc_dict[key_base+'-x'] = spaces.Discrete(env.game.map.size[0])
        self.desc_dict[key_base+'-y'] = spaces.Discrete(env.game.map.size[1])
        self.desc_dict[key_base+'-owner'] = spaces.Discrete(3)
        self.desc_dict[key_base+'-buildings'] = spaces.MultiBinary(self.total_buildings_num)
        self.desc_dict[key_base+'-creature-bank1'] = spaces.Discrete(1000)
        self.desc_dict[key_base+'-creature-bank2'] = spaces.Discrete(1000)
        self.desc_dict[key_base+'-creature-bank3'] = spaces.Discrete(1000)
        self.desc_dict[key_base+'-creature-bank4'] = spaces.Discrete(1000)
        self.desc_dict[key_base+'-creature-bank5'] = spaces.Discrete(1000)
        self.desc_dict[key_base+'-creature-bank6'] = spaces.Discrete(1000)
        self.desc_dict[key_base+'-creature-bank7'] = spaces.Discrete(1000)
        self.desc_dict[key_base+'-army1type'] = spaces.Discrete(self._total_unit_types)
        self.desc_dict[key_base+'-army1num'] =  spaces.Discrete(HOMMArmyStack.MAX_IN_STACK)
        self.desc_dict[key_base+'-army2type'] = spaces.Discrete(self._total_unit_types)
        self.desc_dict[key_base+'-army2num'] =  spaces.Discrete(HOMMArmyStack.MAX_IN_STACK)
        self.desc_dict[key_base+'-army3type'] = spaces.Discrete(self._total_unit_types)
        self.desc_dict[key_base+'-army3num'] =  spaces.Discrete(HOMMArmyStack.MAX_IN_STACK)
        self.desc_dict[key_base+'-army4type'] = spaces.Discrete(self._total_unit_types)
        self.desc_dict[key_base+'-army4num'] =  spaces.Discrete(HOMMArmyStack.MAX_IN_STACK)
        self.desc_dict[key_base+'-army5type'] = spaces.Discrete(self._total_unit_types)
        self.desc_dict[key_base+'-army5num'] =  spaces.Discrete(HOMMArmyStack.MAX_IN_STACK)
        self.desc_dict[key_base+'-army6type'] = spaces.Discrete(self._total_unit_types)
        self.desc_dict[key_base+'-army6num'] =  spaces.Discrete(HOMMArmyStack.MAX_IN_STACK)
        self.desc_dict[key_base+'-army7type'] = spaces.Discrete(self._total_unit_types)
        self.desc_dict[key_base+'-army7num'] =  spaces.Discrete(HOMMArmyStack.MAX_IN_STACK)
        
    def __neutral_desc__(self, env:HOMMGymEnv, idx:int) -> list:
        key_base = f'neutral{idx+1}'
        self.desc_dict[key_base+'-x'] = spaces.Discrete(env.game.map.size[0])
        self.desc_dict[key_base+'-y'] = spaces.Discrete(env.game.map.size[1])
        self.desc_dict[key_base+'-army1type'] = spaces.Discrete(self._total_unit_types)
        self.desc_dict[key_base+'-army1num'] =  spaces.Discrete(HOMMArmyStack.MAX_IN_STACK)
        self.desc_dict[key_base+'-army2type'] = spaces.Discrete(self._total_unit_types)
        self.desc_dict[key_base+'-army2num'] =  spaces.Discrete(HOMMArmyStack.MAX_IN_STACK)
        self.desc_dict[key_base+'-army3type'] = spaces.Discrete(self._total_unit_types)
        self.desc_dict[key_base+'-army3num'] =  spaces.Discrete(HOMMArmyStack.MAX_IN_STACK)
        

    def GetSpace(self, env:HOMMGymEnv) -> Space:
        
        # map tiles, offset by 1 because 0 will mean not visible to current player
        self.desc_dict['map'] = spaces.Box(low=0, high=1+len(TileTypesByName), shape=env.game.map.size, dtype=int8)
        self.desc_dict['day'] = spaces.Discrete(env.game.max_day+2)
        self.desc_dict['current-player'] = spaces.Discrete(env.game.num_players)
        self.desc_dict['gold'] = spaces.Discrete(100_000)
        self.desc_dict['wood'] = spaces.Discrete(1_000)
        self.desc_dict['ore'] = spaces.Discrete(1_000)
        self.desc_dict['mercury'] = spaces.Discrete(500)
        self.desc_dict['sulfur'] = spaces.Discrete(500)
        self.desc_dict['crystal'] = spaces.Discrete(500)
        self.desc_dict['gems'] = spaces.Discrete(500)
        
        self.__hero_desc__(env, idx=0, own=True) # own hero 1
        self.__hero_desc__(env, idx=1, own=True) # own hero 2
        self.__hero_desc__(env, idx=2, own=True) # own hero 3
        self.__hero_desc__(env, idx=3, own=True) # own hero 4
        
        self.__hero_desc__(env, idx=0, own=False) # enemy hero 1
        self.__hero_desc__(env, idx=1, own=False) # enemy hero 2
        self.__hero_desc__(env, idx=2, own=False) # enemy hero 3
        self.__hero_desc__(env, idx=3, own=False) # enemy hero 4
        
        self.__town_desc__(env, idx=0, own=True) # own town 1
        self.__town_desc__(env, idx=1, own=True) # own town 2
        self.__town_desc__(env, idx=2, own=True) # own town 3
        self.__town_desc__(env, idx=3, own=True) # own town 4

        self.__town_desc__(env, idx=0, own=False) # other town 1
        self.__town_desc__(env, idx=1, own=False) # other town 2
        self.__town_desc__(env, idx=2, own=False) # other town 3
        self.__town_desc__(env, idx=3, own=False) # other town 4

        # neutral armies are generated with at most 3 stacks
        
        self.__neutral_desc__(env, idx= 0) # neutral army  1
        self.__neutral_desc__(env, idx= 1) # neutral army  2
        self.__neutral_desc__(env, idx= 2) # neutral army  3
        self.__neutral_desc__(env, idx= 3) # neutral army  4
        self.__neutral_desc__(env, idx= 4) # neutral army  5
        self.__neutral_desc__(env, idx= 5) # neutral army  6
        self.__neutral_desc__(env, idx= 6) # neutral army  7
        self.__neutral_desc__(env, idx= 7) # neutral army  8
        self.__neutral_desc__(env, idx= 8) # neutral army  9
        self.__neutral_desc__(env, idx= 9) # neutral army 10
        self.__neutral_desc__(env, idx=10) # neutral army 11
        self.__neutral_desc__(env, idx=11) # neutral army 12
        self.__neutral_desc__(env, idx=12) # neutral army 13
        self.__neutral_desc__(env, idx=13) # neutral army 14
        self.__neutral_desc__(env, idx=14) # neutral army 15
        self.__neutral_desc__(env, idx=15) # neutral army 16
        
        # hero leveling up
        self.desc_dict['herolevelup-idx'] = spaces.Discrete(5) # hero 1-4, 0=None
        self.desc_dict['herolevelup-choice1'] = spaces.Discrete(1+len(HeroSkills)) # skill choices, 0=None
        self.desc_dict['herolevelup-choice2'] = spaces.Discrete(1+len(HeroSkills))

        # current selection:
        self.desc_dict['selectedhero-idx'] = spaces.Discrete(5) # hero 1-4, 0=None
        self.desc_dict['selectedtown-idx'] = spaces.Discrete(5) # town 1-4, 0=None

        return spaces.Dict(self.desc_dict)
    
    def __army_stack_obs__(self, army:HOMMArmy, idx:int, key_base:str):
        if army and len(army.stacks) > idx:
            self.obs_dict[f'{key_base}-army{idx+1}type'] = army.stacks[idx].unit_type
            self.obs_dict[f'{key_base}-army{idx+1}num'] =  army.stacks[idx].num
        else:
            self.obs_dict[f'{key_base}-army{idx+1}type'] = 0
            self.obs_dict[f'{key_base}-army{idx+1}num'] =  0
    def __hero_obs__(self, env:HOMMGymEnv, hero_idx:int, player_idx:int=0, own:bool=True):
        key_base = f'{"own" if own else "enemy"}hero{hero_idx+1}'
        player = env.game.map.players[player_idx]
        enemy = env.game.map.players[player_idx - 1]
        hero = None
        can_see = (own and len(player.heroes)>hero_idx) or (not own and len(enemy.heroes)>hero_idx and player.CanSee(enemy.heroes[hero_idx].x, enemy.heroes[hero_idx].y))
        if can_see:
            hero = player.heroes[hero_idx] if own else enemy.heroes[hero_idx]
        
        self.obs_dict[f'{key_base}-x'] = hero.x if hero else 0
        self.obs_dict[f'{key_base}-y'] = hero.y if hero else 0
        self.obs_dict[f'{key_base}-attack'] = hero.attack if hero else 0
        self.obs_dict[f'{key_base}-defense'] = hero.defense if hero else 0
        self.obs_dict[f'{key_base}-power'] = hero.power if hero else 0
        self.obs_dict[f'{key_base}-knowledge'] = hero.knowledge if hero else 0
        self.obs_dict[f'{key_base}-mana'] = hero.curr_mana if hero else 0
        self.obs_dict[f'{key_base}-movement'] = hero.curr_movement if hero else 0
        self.obs_dict[f'{key_base}-skills'] = [hero.GetSkillLevel(skill_id) if can_see else 0 for skill_id in range(len(HeroSkills))]
        self.obs_dict[f'{key_base}-spells'] = [1 if can_see and spell_id in hero.spells else 0 for spell_id in range(len(HeroSpells))] # should this be tuple?
        self.__army_stack_obs__(hero.army if hero else None, 0, key_base=key_base)
        self.__army_stack_obs__(hero.army if hero else None, 1, key_base=key_base)
        self.__army_stack_obs__(hero.army if hero else None, 2, key_base=key_base)
        self.__army_stack_obs__(hero.army if hero else None, 3, key_base=key_base)
        self.__army_stack_obs__(hero.army if hero else None, 4, key_base=key_base)
        self.__army_stack_obs__(hero.army if hero else None, 5, key_base=key_base)
        self.__army_stack_obs__(hero.army if hero else None, 6, key_base=key_base)
    def __town_obs__(self, env:HOMMGymEnv, town_idx:int, player_idx:int=0, own:bool=True) -> list:
        key_base = f'{"own" if own else "other"}town{town_idx+1}'
        player = env.game.map.players[player_idx]
        other_towns = [t for t in env.game.map.towns if t.player_idx != player_idx]
        town:TownBase|None = None
        can_see = (own and len(player.towns)>town_idx) or (not own and len(other_towns)>town_idx and player.CanSee(other_towns[town_idx].x, other_towns[town_idx].y))
        if can_see:
            town = player.towns[town_idx] if own else other_towns[town_idx]
        
        self.obs_dict[f'{key_base}-x'] = town.x if town else 0
        self.obs_dict[f'{key_base}-y'] = town.y if town else 0
        self.obs_dict[f'{key_base}-owner'] = 1 + town.player_idx if can_see else 0
        self.obs_dict[f'{key_base}-buildings'] = [1 if can_see and building in town.buildings else 0 for building in self.buildings_list]
        self.obs_dict[f'{key_base}-creature-bank1'] = town.creature_bank[0] if can_see else 0
        self.obs_dict[f'{key_base}-creature-bank2'] = town.creature_bank[1] if can_see else 0
        self.obs_dict[f'{key_base}-creature-bank3'] = town.creature_bank[2] if can_see else 0
        self.obs_dict[f'{key_base}-creature-bank4'] = town.creature_bank[3] if can_see else 0
        self.obs_dict[f'{key_base}-creature-bank5'] = town.creature_bank[4] if can_see else 0
        self.obs_dict[f'{key_base}-creature-bank6'] = town.creature_bank[5] if can_see else 0
        self.obs_dict[f'{key_base}-creature-bank7'] = town.creature_bank[6] if can_see else 0
        self.__army_stack_obs__(town.army if can_see else None, 0, key_base=key_base)
        self.__army_stack_obs__(town.army if can_see else None, 1, key_base=key_base)
        self.__army_stack_obs__(town.army if can_see else None, 2, key_base=key_base)
        self.__army_stack_obs__(town.army if can_see else None, 3, key_base=key_base)
        self.__army_stack_obs__(town.army if can_see else None, 4, key_base=key_base)
        self.__army_stack_obs__(town.army if can_see else None, 5, key_base=key_base)
        self.__army_stack_obs__(town.army if can_see else None, 6, key_base=key_base)
    def __neutral_obs__(self, env:HOMMGymEnv, neutral_idx:int, player_idx:int=0) -> list:
        key_base = f'neutral{neutral_idx+1}'
        player = env.game.map.players[player_idx]
        neutral:HOMMArmy = env.game.map.neutral_armies[neutral_idx] if len(env.game.map.neutral_armies) > neutral_idx else None
        can_see = player.CanSee(neutral.x, neutral.y) if neutral else False
        self.obs_dict[f'{key_base}-x'] = neutral.x if can_see else 0
        self.obs_dict[f'{key_base}-y'] = neutral.y if can_see else 0
        self.__army_stack_obs__(neutral if can_see else None, 0, key_base=key_base)
        self.__army_stack_obs__(neutral if can_see else None, 1, key_base=key_base)
        self.__army_stack_obs__(neutral if can_see else None, 2, key_base=key_base)

    def GetObservation(self, env:HOMMGymEnv, last_action_was_accepted:bool=True, last_action_was_valid:bool=True):
        assert len(env.game.map.players) == 2
        player = env.game.map.players[env.game.map.curr_player_idx] if not env.game.map.hero_leveling_up else env.game.map.players[env.game.map.hero_leveling_up.player_idx]
        return_previous = self.__last_active_player_idx != player.idx and not (last_action_was_accepted and last_action_was_valid)
        if not return_previous:
            other_towns = [t for t in env.game.map.towns if t.player_idx != player.idx]
            assert len(other_towns) <= 4
            assert len(env.game.map.neutral_armies) <= 16, 'template error: there are more than 16 neutral armies'

            # map, masked by what is visible to current player
            self.obs_dict['map'] = (env.game.map.tiles[0,] + 1) * player.visibility.astype(int)
            self.obs_dict['day'] = env.game.map.day
            self.obs_dict['current-player'] = env.game.map.curr_player_idx
            self.obs_dict['gold'] = min(player.resources[0], 99_999)
            self.obs_dict['wood'] = min(player.resources[1], 999)
            self.obs_dict['ore'] = min(player.resources[2], 999)
            self.obs_dict['mercury'] = min(player.resources[3], 499)
            self.obs_dict['sulfur'] = min(player.resources[4], 499)
            self.obs_dict['crystal'] = min(player.resources[5], 499)
            self.obs_dict['gems'] = min(player.resources[6], 499)

            self.__hero_obs__(env, hero_idx=0, player_idx=player.idx, own=True)
            self.__hero_obs__(env, hero_idx=1, player_idx=player.idx, own=True)
            self.__hero_obs__(env, hero_idx=2, player_idx=player.idx, own=True)
            self.__hero_obs__(env, hero_idx=3, player_idx=player.idx, own=True)

            self.__hero_obs__(env, hero_idx=0, player_idx=player.idx, own=False)
            self.__hero_obs__(env, hero_idx=1, player_idx=player.idx, own=False)
            self.__hero_obs__(env, hero_idx=2, player_idx=player.idx, own=False)
            self.__hero_obs__(env, hero_idx=3, player_idx=player.idx, own=False)
            
            self.__town_obs__(env, town_idx=0, player_idx=player.idx, own=True)
            self.__town_obs__(env, town_idx=1, player_idx=player.idx, own=True)
            self.__town_obs__(env, town_idx=2, player_idx=player.idx, own=True)
            self.__town_obs__(env, town_idx=3, player_idx=player.idx, own=True)

            self.__town_obs__(env, town_idx=0, player_idx=player.idx, own=False)
            self.__town_obs__(env, town_idx=1, player_idx=player.idx, own=False)
            self.__town_obs__(env, town_idx=2, player_idx=player.idx, own=False)
            self.__town_obs__(env, town_idx=3, player_idx=player.idx, own=False)

            self.__neutral_obs__(env, neutral_idx= 0, player_idx=player.idx)
            self.__neutral_obs__(env, neutral_idx= 1, player_idx=player.idx)
            self.__neutral_obs__(env, neutral_idx= 2, player_idx=player.idx)
            self.__neutral_obs__(env, neutral_idx= 3, player_idx=player.idx)
            self.__neutral_obs__(env, neutral_idx= 4, player_idx=player.idx)
            self.__neutral_obs__(env, neutral_idx= 5, player_idx=player.idx)
            self.__neutral_obs__(env, neutral_idx= 6, player_idx=player.idx)
            self.__neutral_obs__(env, neutral_idx= 7, player_idx=player.idx)
            self.__neutral_obs__(env, neutral_idx= 8, player_idx=player.idx)
            self.__neutral_obs__(env, neutral_idx= 9, player_idx=player.idx)
            self.__neutral_obs__(env, neutral_idx=10, player_idx=player.idx)
            self.__neutral_obs__(env, neutral_idx=11, player_idx=player.idx)
            self.__neutral_obs__(env, neutral_idx=12, player_idx=player.idx)
            self.__neutral_obs__(env, neutral_idx=13, player_idx=player.idx)
            self.__neutral_obs__(env, neutral_idx=14, player_idx=player.idx)
            self.__neutral_obs__(env, neutral_idx=15, player_idx=player.idx)

            self.obs_dict['herolevelup-idx'] = 1+player.heroes.index(env.game.map.hero_leveling_up) if env.game.map.hero_leveling_up else 0
            self.obs_dict['herolevelup-choice1'] = 1+env.game.map.hero_leveling_up.GetSkillChoices()[0] if env.game.map.hero_leveling_up else 0
            self.obs_dict['herolevelup-choice2'] = 1+env.game.map.hero_leveling_up.GetSkillChoices()[1] if env.game.map.hero_leveling_up else 0

            self.obs_dict['selectedhero-idx'] = player.sel_hero_idx
            self.obs_dict['selectedtown-idx'] = player.sel_town_idx

        return self.obs_dict

class GameObserverSelectedHeroTownFlat(GameObserverSelectedHeroTown):
    def GetSpace(self, env: HOMMGymEnv) -> Space:
        return spaces.flatten_space(super().GetSpace(env))
    def GetObservation(self, env: HOMMGymEnv, last_action_was_accepted: bool = True, last_action_was_valid: bool = True):
        return spaces.flatten(super().GetSpace(env),
            super().GetObservation(env,
                last_action_was_accepted,
                last_action_was_valid),
            )

class GameActionMapperSelection(GameActionMapper):
    def __init__(self, env:HOMMGymEnv) -> None:
        assert isinstance(env.observer, GameObserverSelectedHeroTown)
        self.map_size = env.game.map.size

        #['ActionMoveHero', 'ActionBuild', 'ActionRecruitArmy', 'ActionTransferArmy', 'ActionRecruitHero', 'ActionSkillChoice', 'ActionEndTurn']
        self.action_types = [cls.__name__ for cls in HOMMAction.__subclasses__() if cls != 'BattleAction']

        self.buildings_list = list(TownTypes['Castle']['Buildings'])
        self.num_buildings_per_town = len(self.buildings_list)
        
        self.total_actions_num = 0

        self.action_build_start = self.total_actions_num
        self.total_actions_num += self.num_buildings_per_town
        self.action_build_end = self.total_actions_num-1

        self.action_recruit_army_start = self.total_actions_num
        self.total_actions_num += 14 # 14 because each town has at most 14 units (7 levels + upgrades for each)
        self.action_recruit_army_end = self.total_actions_num-1

        self.action_transfer_army_start = self.total_actions_num
        self.total_actions_num += 7 * 2 # 0-6 idx of army stack in hero army, 7-13 idx of army stack in town army
        self.action_transfer_army_end = self.total_actions_num-1

        self.action_recruit_hero = self.total_actions_num
        self.total_actions_num += 1

        self.action_skill_choice_start = self.total_actions_num
        self.total_actions_num += 2
        self.action_skill_choice_end = self.total_actions_num-1

        self.action_move_hero_start = self.total_actions_num
        self.total_actions_num += env.game.map.size[0] * env.game.map.size[1] # consider making this smaller and centered aroung the hero
        self.action_move_hero_end = self.total_actions_num-1

        self.action_end_turn = self.total_actions_num
        self.total_actions_num += 1

        self.action_selection_start = self.total_actions_num
        self.total_actions_num += 8 # 0-3 change hero selected, 4-7 change town selected
        self.action_selection_end = self.total_actions_num-1

    def GetActionSpace(self, env:HOMMGymEnv) -> Space:
        return DiscreteMasked(self.total_actions_num) # spaces.Discrete(self.total_actions_num)

    def GetValidActionsMask(self, env:HOMMGymEnv):
        if env.game.map.hero_leveling_up:
            mask = np.zeros(shape=(self.total_actions_num), dtype=bool) # [False] * self.total_actions_num
            mask[self.action_skill_choice_start:self.action_skill_choice_end+1] = True
        elif env.game.actions_this_turn >= env.game.max_actions_turn-1:
            # force this action this way
            mask = np.zeros(shape=(self.total_actions_num), dtype=bool)
            mask[self.action_end_turn] = True
        else:
            mask = np.ones(shape=(self.total_actions_num), dtype=bool) # [True] * self.total_actions_num
            mask[self.action_skill_choice_start:self.action_skill_choice_end+1] = False
            player = env.game.map.players[env.game.map.curr_player_idx]
            hero:Hero = None
            town:TownBase = None
            if player.sel_hero_idx == 0 or player.sel_town_idx == 0:
                mask[self.action_transfer_army_start:self.action_transfer_army_end+1] = False
            if player.sel_hero_idx == 0:
                mask[self.action_move_hero_start:self.action_move_hero_end+1] = False
            else:
                # white-list only explored positions to move hero
                # this should be revisited when implementing map spells such as Dimension Door and Fly
                hero = player.heroes[player.sel_hero_idx-1]
                xx, yy = np.where(player.visibility)
                mask[self.action_move_hero_start:self.action_move_hero_end+1] = False
                if hero:
                    for x,y in zip(xx, yy):
                        mask[x * env.game.map.size[1] + y + self.action_move_hero_start] = env.game.map.CanStepOn(hero, x, y)
                    mask[hero.x * env.game.map.size[1] + hero.y + self.action_move_hero_start] = False
            if player.sel_town_idx == 0:
                mask[self.action_build_start:self.action_build_end+1] = False
                mask[self.action_recruit_army_start:self.action_recruit_army_end+1] = False
                mask[self.action_recruit_hero] = False
            else:
                town = player.towns[player.sel_town_idx-1]
                if town and town.built_today:
                    mask[self.action_build_start:self.action_build_end+1] = False
            if not player.heroes:
                mask[self.action_selection_start:self.action_selection_end+4] = False
            if not player.towns:
                mask[self.action_selection_start+4:self.action_selection_end+1] = False
        discreteMasked:DiscreteMasked = env.action_space
        discreteMasked.UpdateMask(mask)
        return mask #return [a for a in range(self.total_actions_num) if mask[a]]

    def UnmapAction(self, env:HOMMGymEnv, action) -> HOMMAction:
        obs:GameObserverSelectedHeroTown = env.observer
        player = env.game.map.players[env.game.map.curr_player_idx] if not env.game.map.hero_leveling_up else env.game.map.players[env.game.map.hero_leveling_up.player_idx]
        assert obs
        if self.action_build_start <= action <= self.action_build_end:
            if player.sel_town_idx > 0:
                building_idx = action - self.action_build_start
                return ActionBuild(town_idx=player.sel_town_idx-1, building_name=self.buildings_list[building_idx])
        elif self.action_recruit_army_start <= action <= self.action_recruit_army_end:
            if player.sel_town_idx > 0:
                unit_type_idx = action - self.action_recruit_army_start
                unit_type_id = TownTypes['Castle']['Units'][unit_type_idx]
                return ActionRecruitArmy(town_idx=player.sel_town_idx-1, unit_type=unit_type_id, amount=1000)
        elif self.action_transfer_army_start <= action <= self.action_transfer_army_end:
            if player.sel_town_idx > 0 and player.sel_hero_idx > 0:
                idx = action - self.action_transfer_army_start
                assert 0 <= idx < 14
                if idx < 7: # hero to town
                    return ActionTransferArmy(stack_idx=idx, src_hero_idx=player.sel_hero_idx-1, dest_town_idx=player.sel_town_idx-1, amount=1000)
                else: # town to hero
                    return ActionTransferArmy(stack_idx=idx-7, src_town_idx=player.sel_hero_idx-1, dest_hero_idx=player.sel_town_idx-1, amount=1000)
        elif action == self.action_recruit_hero:
            if player.sel_town_idx > 0:
                return ActionRecruitHero(town_idx=player.sel_town_idx-1)
        elif self.action_skill_choice_start <= action <= self.action_skill_choice_end:
            rest = action - self.action_skill_choice_start
            return ActionSkillChoice(option=rest)
        elif self.action_move_hero_start <= action <= self.action_move_hero_end:
            if player.sel_hero_idx > 0:
                rest = action - self.action_move_hero_start
                x = rest // env.game.map.size[1]
                y = rest % env.game.map.size[1]
                return ActionMoveHero(hero_idx=player.sel_hero_idx-1, dest=(x, y))
        elif action == self.action_end_turn:
            return ActionEndTurn()
        elif self.action_selection_start <= action <= self.action_selection_end:
            rest = action - self.action_selection_start
            if rest < 4: # select a hero
                return  ActionChangeSelection(sel_hero_idx = rest)
            else: # select town
                return ActionChangeSelection(sel_hero_idx = rest - 4)
        return None

class GameActionMapperSelectionReduced(GameActionMapper):
    MOVE_ACTION_DELTAS = [
        (-1,-1), (-1, 0), (-1,+1),
        ( 0,-1),          ( 0,+1),
        (+1,-1), (+1, 0), (+1,+1),
    ]
    def __init__(self, env:HOMMGymEnv) -> None:
        assert isinstance(env.observer, GameObserverSelectedHeroTown)
        self.map_size = env.game.map.size

        env.game.autoskill_existing[env.ML_player_idx] = True

        self.buildings_list = list(TownTypes['Castle']['Buildings'])
        self.num_buildings_per_town = len(self.buildings_list)
        
        self.total_actions_num = 0

        self.action_build_start = self.total_actions_num
        self.total_actions_num += self.num_buildings_per_town
        self.action_build_end = self.total_actions_num-1

        self.action_recruit_army = self.total_actions_num
        self.total_actions_num += 1 # only one action: try and recruit everything (or as much as there are resources)

        self.action_transfer_army_start = self.total_actions_num
        self.total_actions_num += 2 # only two actions: hero to town, town to hero (try to transfer everything)
        self.action_transfer_army_end = self.total_actions_num-1

        self.action_recruit_hero = self.total_actions_num
        self.total_actions_num += 1

        self.action_move_hero_start = self.total_actions_num
        self.total_actions_num += len(self.MOVE_ACTION_DELTAS)
        self.action_move_hero_end = self.total_actions_num-1

        self.action_end_turn = self.total_actions_num
        self.total_actions_num += 1

        self.action_selection_start = self.total_actions_num
        self.total_actions_num += 8 # 0-3 change hero selected, 4-7 change town selected
        self.action_selection_end = self.total_actions_num-1

    def GetActionSpace(self, env:HOMMGymEnv) -> Space:
        return DiscreteMasked(self.total_actions_num)

    def GetValidActionsMask(self, env:HOMMGymEnv):
        env.game.autoskill_existing[env.ML_player_idx] = True # need to do this again due to successive reset()
        mask = np.ones(shape=(self.total_actions_num), dtype=bool)
        player = env.game.map.players[env.game.map.curr_player_idx]
        if len(player.heroes) >= env.game.map.MAX_PLAYER_HEROES:
            mask[self.action_recruit_hero] = False
        if player.sel_hero_idx == 0:
            mask[self.action_move_hero_start:self.action_build_start+1] = False
        else:
            hero = player.heroes[player.sel_hero_idx-1]
            if hero.curr_movement <= 0:
                mask[self.action_move_hero_start:self.action_build_start+1] = False
            for pos_idx in range(len(self.MOVE_ACTION_DELTAS)):
                dx,dy = self.MOVE_ACTION_DELTAS[pos_idx]
                x, y = hero.x+dx, hero.y+dy
                if not (env.game.map.IsInBounds(x, y) and env.game.map.CanStepOn(hero, x, y)):
                    mask[self.action_move_hero_start+pos_idx] = False
        if player.sel_town_idx == 0:
            mask[self.action_build_start:self.action_build_end+1] = False
            mask[self.action_recruit_army] = False
            mask[self.action_recruit_hero] = False
        else:
            town:TownBase = player.towns[player.sel_town_idx-1]
            if town:
                if town.built_today:
                    mask[self.action_build_start:self.action_build_end+1] = False
                else:
                    built_idxes = [self.buildings_list.index(b) for b in town.buildings]
                    mask[built_idxes] = False
                    unaffordable_idxes = [idx for idx, b in enumerate(self.buildings_list) if not player.CanAffort(TownTypes['Castle']['Buildings'][b]['cost'])]
                    mask[unaffordable_idxes] = False
                if next((h for h in player.heroes if h.x==town.x and h.y==town.y), None):
                    mask[self.action_recruit_hero] = False
        # disable selecting non-existing heroes
        mask[self.action_selection_start+(4-len(player.heroes)) : self.action_selection_start+4] = False
        # disable selecting non-existing towns
        mask[self.action_selection_start+4+(4-len(player.towns)) : self.action_selection_start+8] = False
        # disable selecting what is already selected
        if player.sel_hero_idx > 0:
            mask[self.action_selection_start+player.sel_hero_idx-1] = False
        if player.sel_town_idx > 0:
            mask[self.action_selection_start+4+player.sel_town_idx-1] = False
        discreteMasked:DiscreteMasked = env.action_space
        discreteMasked.UpdateMask(mask)
        return mask

    def UnmapAction(self, env:HOMMGymEnv, action) -> HOMMAction:
        obs:GameObserverSelectedHeroTown = env.observer
        player = env.game.map.players[env.game.map.curr_player_idx] if not env.game.map.hero_leveling_up else env.game.map.players[env.game.map.hero_leveling_up.player_idx]
        assert obs
        if self.action_build_start <= action <= self.action_build_end:
            if player.sel_town_idx > 0:
                building_idx = action - self.action_build_start
                return ActionBuild(town_idx=player.sel_town_idx-1, building_name=self.buildings_list[building_idx])
        elif self.action_recruit_army == action:
            if player.sel_town_idx > 0:
                return ActionRecruitArmy(town_idx=player.sel_town_idx-1, unit_type=-1, amount=1000)
        elif self.action_transfer_army_start <= action <= self.action_transfer_army_end:
            if player.sel_hero_idx > 0 and player.sel_town_idx > 0:
                if self.action_transfer_army_start == action:
                    return ActionTransferArmy(stack_idx=-1, amount=1000,
                        src_hero_idx=player.sel_hero_idx-1,
                        dest_town_idx=player.sel_town_idx-1)
                else:
                    return ActionTransferArmy(stack_idx=-1, amount=1000,
                        src_town_idx=player.sel_town_idx-1,
                        dest_hero_idx=player.sel_hero_idx-1)
        elif self.action_recruit_hero == action:
            if player.sel_town_idx > 0:
                return ActionRecruitHero(town_idx=player.sel_town_idx-1)
        elif self.action_move_hero_start <= action <= self.action_move_hero_end:
            rest = action - self.action_move_hero_start
            dx,dy = self.MOVE_ACTION_DELTAS[rest]
            if player.sel_hero_idx > 0:
                hero = player.heroes[player.sel_hero_idx-1]
                return ActionMoveHero(hero_idx=player.sel_hero_idx-1, dest=(hero.x+dx, hero.y+dy))
        elif self.action_end_turn == action:
            return ActionEndTurn()
        elif self.action_selection_start <= action <= self.action_selection_end:
            rest = action - self.action_selection_start
            if rest < 4: # select a hero
                return  ActionChangeSelection(sel_hero_idx = rest)
            else: # select town
                return ActionChangeSelection(sel_hero_idx = rest - 4)
        return None
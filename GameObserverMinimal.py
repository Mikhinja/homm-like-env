from typing import OrderedDict
from gym import Space, spaces
from numpy import int16, int8
from GameObserverSelectionFlat import GameObserverSelectedHeroTown
from HOMM.HOMMUnitTypes import UnitUtils
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

class GameObserverMinimal(GameObserverSelectedHeroTown):
    BUILDINGS_LIST = ['Capitol', 'Monastery', 'Portal of Glory']
    def __init__(self) -> None:
        super().__init__()
        self.buildings_list = GameObserverMinimal.BUILDINGS_LIST
        self.total_buildings = len(self.buildings_list)

    def __town_desc__(self, env:HOMMGymEnv, idx:int, player_idx:int=0):
        key_base = f'town{idx+1}'
        self.desc_dict[key_base+'-x'] = spaces.Discrete(env.game.map.size[0])
        self.desc_dict[key_base+'-y'] = spaces.Discrete(env.game.map.size[1])
        self.desc_dict[key_base+'-owner'] = spaces.Discrete(3)
        # this next one is not quite right, because by minimizing we are eliminating information from the observation,
        # but for the minimalist approach this shouldn't matter much
        self.desc_dict[key_base+'-buildings'] = spaces.MultiBinary(self.total_buildings)
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

    def GetSpace(self, env) -> Space:
        assert env.max_heroes == 1
        assert len(env.game.map.towns) <= 4
        # map tiles, offset by 1 because 0 will mean not visible to current player
        self.desc_dict['map-x'] = spaces.Discrete(env.game.map.size[0]+1)
        self.desc_dict['map-y'] = spaces.Discrete(env.game.map.size[1]+1)
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

        self.__hero_desc__(env, idx=0, own=True) # own hero - there is only one

        self.__hero_desc__(env, idx=0, own=False) # enemy hero - there is only one

        # there can only be 4 towns on the HardcodedTemplate
        self.__town_desc__(env, idx=0, player_idx=0) # town 1
        self.__town_desc__(env, idx=1, player_idx=0) # town 2
        self.__town_desc__(env, idx=2, player_idx=0) # town 3
        self.__town_desc__(env, idx=3, player_idx=0) # town 4

        # neutral armies are generated with at most 3 stacks
        
        self.__neutral_desc__(env, idx= 0) # neutral army  1
        self.__neutral_desc__(env, idx= 1) # neutral army  2
        self.__neutral_desc__(env, idx= 2) # neutral army  3
        self.__neutral_desc__(env, idx= 3) # neutral army  4
        self.__neutral_desc__(env, idx= 4) # neutral army  5
        self.__neutral_desc__(env, idx= 5) # neutral army  6
        self.__neutral_desc__(env, idx= 6) # neutral army  7
        self.__neutral_desc__(env, idx= 7) # neutral army  8

        return spaces.Dict(self.desc_dict)

    def __town_obs__(self, env:HOMMGymEnv, town_idx:int, player_idx:int=0) -> list:
        key_base = f'town{town_idx+1}'
        player = env.game.map.players[player_idx]
        all_towns = [t for t in env.game.map.towns]
        town:TownBase|None = all_towns[town_idx] if len(all_towns)>town_idx else None
        can_see = player.CanSee(town.x, town.y) if town else False
        
        self.obs_dict[f'{key_base}-x'] = town.x if can_see else 0
        self.obs_dict[f'{key_base}-y'] = town.y if can_see else 0
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

    def GetObservation(self, env, last_action_was_accepted: bool = True, last_action_was_valid: bool = True):
        assert len(env.game.map.players) == 2
        player = env.game.map.players[env.game.map.curr_player_idx] if not env.game.map.hero_leveling_up else env.game.map.players[env.game.map.hero_leveling_up.player_idx]
        other_towns = [t for t in env.game.map.towns if t.player_idx != player.idx]
        assert len(other_towns) <= 4
        assert len(env.game.map.neutral_armies) <= 16, 'template error: there are more than 16 neutral armies'

        # map, masked by what is visible to current player
        self.obs_dict['map-x'] = env.game.map.size[0]
        self.obs_dict['map-y'] = env.game.map.size[1]
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

        self.__hero_obs__(env, hero_idx=0, player_idx=player.idx, own=False)

        self.__town_obs__(env, town_idx=0, player_idx=player.idx)
        self.__town_obs__(env, town_idx=1, player_idx=player.idx)
        self.__town_obs__(env, town_idx=2, player_idx=player.idx)
        self.__town_obs__(env, town_idx=3, player_idx=player.idx)

        self.__neutral_obs__(env, neutral_idx= 0, player_idx=player.idx)
        self.__neutral_obs__(env, neutral_idx= 1, player_idx=player.idx)
        self.__neutral_obs__(env, neutral_idx= 2, player_idx=player.idx)
        self.__neutral_obs__(env, neutral_idx= 3, player_idx=player.idx)
        self.__neutral_obs__(env, neutral_idx= 4, player_idx=player.idx)
        self.__neutral_obs__(env, neutral_idx= 5, player_idx=player.idx)
        self.__neutral_obs__(env, neutral_idx= 6, player_idx=player.idx)
        self.__neutral_obs__(env, neutral_idx= 7, player_idx=player.idx)

        return self.obs_dict

class GameObserverMinimalFlat(GameObserverMinimal):
    def GetSpace(self, env: HOMMGymEnv) -> Space:
        return spaces.flatten_space(super().GetSpace(env))
    def GetObservation(self, env: HOMMGymEnv, last_action_was_accepted: bool = True, last_action_was_valid: bool = True):
        return spaces.flatten(super().GetSpace(env),
            super().GetObservation(env,
                last_action_was_accepted,
                last_action_was_valid),
            )

class GameObserverReallyMinimal(GameObserver):
    def __init__(self) -> None:
        self.desc_dict = OrderedDict()
        self.obs_dict = OrderedDict()
        self.max_AIVal = int(np.log2(3 * UnitUtils.GetAIValue(UnitUtils.GetUnitTypeByName('Archangel'))))
    
    def __hero_desc__(self, env:HOMMGymEnv, idx:int, own:bool=True):
        key_base = f'{"own" if own else "enemy"}hero{idx+1}'
        self.desc_dict[key_base+'-x'] = spaces.Discrete(env.game.map.size[0])
        self.desc_dict[key_base+'-y'] = spaces.Discrete(env.game.map.size[1])
        self.desc_dict[key_base+'-level'] = spaces.Discrete(10) # it's never going to reach level 10 on minimal games
        self.desc_dict[key_base+'-armyStr'] = spaces.Discrete(
            # HOMMArmyStack.MAX_IN_STACK * UnitUtils.GetAIValue(UnitUtils.GetUnitTypeByName('Archangel')))
            2 + self.max_AIVal)

    def __town_desc__(self, env:HOMMGymEnv, idx:int=0, player_idx:int=0):
        key_base = f'town{idx+1}'
        self.desc_dict[key_base+'-x'] = spaces.Discrete(env.game.map.size[0])
        self.desc_dict[key_base+'-y'] = spaces.Discrete(env.game.map.size[1])
        self.desc_dict[key_base+'-owner'] = spaces.Discrete(3)
        self.desc_dict[key_base+'-armyStr'] = spaces.Discrete(
            # HOMMArmyStack.MAX_IN_STACK * UnitUtils.GetAIValue(UnitUtils.GetUnitTypeByName('Archangel')))
            2 + self.max_AIVal)

    
    def __neutral_desc__(self, env:HOMMGymEnv, idx:int) -> list:
        key_base = f'neutral{idx+1}'
        self.desc_dict[key_base+'-x'] = spaces.Discrete(env.game.map.size[0])
        self.desc_dict[key_base+'-y'] = spaces.Discrete(env.game.map.size[1])
        self.desc_dict[key_base+'-armyStr'] = spaces.Discrete(
            # HOMMArmyStack.MAX_IN_STACK * UnitUtils.GetAIValue(UnitUtils.GetUnitTypeByName('Archangel')))
            2 + self.max_AIVal)


    def GetSpace(self, env:HOMMGymEnv) -> Space:
        assert env.max_heroes == 1
        assert len(env.game.map.towns) <= 4

        self.desc_dict['map'] = spaces.Box(low=0, high=1+len(TileTypesByName), shape=env.game.map.size, dtype=int8)
        self.desc_dict['day'] = spaces.Discrete(env.game.max_day+2)
        self.desc_dict['current-player'] = spaces.Discrete(env.game.num_players)

        self.__hero_desc__(env, idx=0, own=True) # own hero - there is only one

        self.__hero_desc__(env, idx=0, own=False) # enemy hero - there is only one

        # there can only be 4 towns on the HardcodedTemplate
        self.__town_desc__(env, idx=0, player_idx=0) # town 1
        self.__town_desc__(env, idx=1, player_idx=0) # town 2
        self.__town_desc__(env, idx=2, player_idx=0) # town 3
        self.__town_desc__(env, idx=3, player_idx=0) # town 4

        self.__neutral_desc__(env, idx= 0) # neutral army  1
        self.__neutral_desc__(env, idx= 1) # neutral army  2
        self.__neutral_desc__(env, idx= 2) # neutral army  3
        self.__neutral_desc__(env, idx= 3) # neutral army  4
        self.__neutral_desc__(env, idx= 4) # neutral army  5
        self.__neutral_desc__(env, idx= 5) # neutral army  6

        return spaces.Dict(self.desc_dict)

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
        self.obs_dict[f'{key_base}-level'] = hero.GetLevel() if hero else 0
        self.obs_dict[f'{key_base}-armyStr'] = min(self.max_AIVal,int(np.log2(hero.army.GetAIVal()))) if hero else 0
    
    def __town_obs__(self, env:HOMMGymEnv, town_idx:int, player_idx:int=0) -> list:
        key_base = f'town{town_idx+1}'
        player = env.game.map.players[player_idx]
        all_towns = [t for t in env.game.map.towns]
        town:TownBase|None = all_towns[town_idx] if len(all_towns)>town_idx else None
        can_see = player.CanSee(town.x, town.y) if town else False
        
        self.obs_dict[f'{key_base}-x'] = town.x if can_see else 0
        self.obs_dict[f'{key_base}-y'] = town.y if can_see else 0
        self.obs_dict[f'{key_base}-owner'] = 1 + town.player_idx if can_see else 0
        self.obs_dict[f'{key_base}-armyStr'] = min(self.max_AIVal,
            int(np.log2(town.army.GetAIVal()))
        ) if can_see and town.army and town.army.GetAIVal()>0 else 0
    
    def __neutral_obs__(self, env:HOMMGymEnv, neutral_idx:int, player_idx:int=0) -> list:
        key_base = f'neutral{neutral_idx+1}'
        player = env.game.map.players[player_idx]
        neutral:HOMMArmy = env.game.map.neutral_armies[neutral_idx] if len(env.game.map.neutral_armies) > neutral_idx else None
        can_see = player.CanSee(neutral.x, neutral.y) if neutral else False
        self.obs_dict[f'{key_base}-x'] = neutral.x if can_see else 0
        self.obs_dict[f'{key_base}-y'] = neutral.y if can_see else 0
        self.obs_dict[f'{key_base}-armyStr'] = min(self.max_AIVal,int(np.log2(neutral.GetAIVal()))) if can_see else 0

    def GetObservation(self, env:HOMMGymEnv, last_action_was_accepted: bool = True, last_action_was_valid: bool = True):
        assert len(env.game.map.players) == 2
        player = env.game.map.players[env.game.map.curr_player_idx] if not env.game.map.hero_leveling_up else env.game.map.players[env.game.map.hero_leveling_up.player_idx]
        other_towns = [t for t in env.game.map.towns if t.player_idx != player.idx]
        assert len(other_towns) <= 4
        assert len(env.game.map.neutral_armies) <= 16, 'template error: there are more than 16 neutral armies'

        # map, masked by what is visible to current player
        self.obs_dict['map'] = (env.game.map.tiles[0,] + 1) * player.visibility.astype(int)
        self.obs_dict['day'] = env.game.map.day
        self.obs_dict['current-player'] = env.game.map.curr_player_idx

        self.__hero_obs__(env, hero_idx=0, player_idx=player.idx, own=True)

        self.__hero_obs__(env, hero_idx=0, player_idx=player.idx, own=False)

        self.__town_obs__(env, town_idx=0, player_idx=player.idx)
        self.__town_obs__(env, town_idx=1, player_idx=player.idx)
        self.__town_obs__(env, town_idx=2, player_idx=player.idx)
        self.__town_obs__(env, town_idx=3, player_idx=player.idx)

        self.__neutral_obs__(env, neutral_idx= 0, player_idx=player.idx)
        self.__neutral_obs__(env, neutral_idx= 1, player_idx=player.idx)
        self.__neutral_obs__(env, neutral_idx= 2, player_idx=player.idx)
        self.__neutral_obs__(env, neutral_idx= 3, player_idx=player.idx)
        self.__neutral_obs__(env, neutral_idx= 4, player_idx=player.idx)
        self.__neutral_obs__(env, neutral_idx= 5, player_idx=player.idx)

        return self.obs_dict

class GameObserverReallyMinimalFlat(GameObserverReallyMinimal):
    def GetSpace(self, env: HOMMGymEnv) -> Space:
        return spaces.flatten_space(super().GetSpace(env))
    def GetObservation(self, env: HOMMGymEnv, last_action_was_accepted: bool = True, last_action_was_valid: bool = True):
        return spaces.flatten(super().GetSpace(env),
            super().GetObservation(env,
                last_action_was_accepted,
                last_action_was_valid),
            )

class GameActionMapperMinimal(GameActionMapper):
    MOVE_ACTION_DELTAS = [
        (-1,-1), (-1, 0), (-1,+1),
        ( 0,-1),          ( 0,+1),
        (+1,-1), (+1, 0), (+1,+1),
    ]
    def __init__(self, env:HOMMGymEnv) -> None:
        #assert isinstance(env.observer, GameObserverMinimal) # is it ok to skip this?
        obs_minimal:GameObserverMinimal = env.observer
        self.map_size = env.game.map.size
        env.game.autoskill_existing[env.ML_player_idx] = True
        self.buildings_list = obs_minimal.buildings_list if isinstance(obs_minimal, GameObserverMinimal) else GameObserverMinimal.BUILDINGS_LIST

        self.total_actions_num = 0

        self.action_build_start = self.total_actions_num
        self.total_actions_num += len(self.buildings_list)
        self.action_build_end = self.total_actions_num-1

        self.action_recruit_army = self.total_actions_num
        self.total_actions_num += 1 # only one action: try and recruit everything (or as much as there are resources)

        self.action_move_hero_start = self.total_actions_num
        self.total_actions_num += len(self.MOVE_ACTION_DELTAS)
        self.action_move_hero_end = self.total_actions_num-1

        self.action_end_turn = self.total_actions_num
        self.total_actions_num += 1

    def GetActionSpace(self, env:HOMMGymEnv) -> Space:
        return DiscreteMasked(self.total_actions_num)
    
    def GetValidActionsMask(self, env:HOMMGymEnv):
        env.game.autoskill_existing[env.ML_player_idx] = True # need to do this again due to successive reset()
        player = env.game.map.players[env.game.map.curr_player_idx]
        mask = np.ones(shape=(self.total_actions_num), dtype=bool)
        if len(player.heroes) == 0:
            mask[self.action_move_hero_start:self.action_move_hero_end+1] = False
        else:
            hero = player.heroes[0] # there is only one
            if hero.curr_movement <= 0:
                mask[self.action_move_hero_start:self.action_move_hero_end+1] = False
            for pos_idx in range(len(self.MOVE_ACTION_DELTAS)):
                dx,dy = self.MOVE_ACTION_DELTAS[pos_idx]
                x, y = hero.x+dx, hero.y+dy
                if not (env.game.map.IsInBounds(x, y) and env.game.map.ValidDestPos(x, y) and player.CanSee(x, y)
                        and hero.curr_movement >= env.game.map.Adj_Dist(hero.x, hero.y, x, y)):
                    mask[self.action_move_hero_start+pos_idx] = False
        if len(player.towns) > 0 and not all(t.built_today for t in player.towns):
            town0 = player.towns[0]
            for idx in range(len(self.buildings_list)):
                if not player.CanAffort(town0.GetCostOfBuilding(self.buildings_list[idx])):
                    mask[self.action_build_start+idx] = False
                elif all(self.buildings_list[idx] in t.buildings for t in player.towns):
                    mask[self.action_build_start+idx] = False
            if all(not any(t.creature_bank) for t in player.towns):
                mask[self.action_recruit_army] = False
        else:
            mask[self.action_build_start:self.action_build_end+1] = False
            mask[self.action_recruit_army] = False
        discreteMasked:DiscreteMasked = env.action_space
        discreteMasked.UpdateMask(mask)
        return mask

    def UnmapAction(self, env:HOMMGymEnv, action) -> HOMMAction|list[HOMMAction]:
        obs:GameObserverMinimal = env.observer
        player = env.game.map.players[env.game.map.curr_player_idx] if not env.game.map.hero_leveling_up else env.game.map.players[env.game.map.hero_leveling_up.player_idx]
        assert obs
        if self.action_build_start <= action <= self.action_build_end:
            rest = action - self.action_build_start
            if len(player.towns) > 1:
                return [ActionBuild(town_idx=idx, building_name=self.buildings_list[rest]) for idx in range(len(player.towns))]
            elif len(player.towns) == 1:
                return ActionBuild(town_idx=0, building_name=self.buildings_list[rest])
        elif self.action_recruit_army == action:
            if len(player.towns) > 0:
                actions = [ActionRecruitArmy(town_idx=idx, unit_type=-1, amount=1000) for idx in range(len(player.towns))]
                hero = player.heroes[0] if player.heroes else None
                town = next((t for t in player.towns if t.x==hero.x and t.y==hero.y), None) if hero else None
                if hero and town:
                    actions.append(ActionTransferArmy(src_town_idx=player.towns.index(town), dest_hero_idx=0, stack_idx=-1, amount=1000))
                elif town and not hero:
                    actions.append(ActionRecruitHero(town_idx=0))
                    actions.append(ActionTransferArmy(src_town_idx=player.towns.index(town), dest_hero_idx=0, stack_idx=-1, amount=1000))
                return actions
        elif self.action_move_hero_start <= action <= self.action_move_hero_end:
            rest = action - self.action_move_hero_start
            dx,dy = self.MOVE_ACTION_DELTAS[rest]
            if len(player.heroes) > 0:
                hero = player.heroes[0] # there is only one
                town = next((t for t in player.towns
                    if (t.x==hero.x and t.y==hero.y) or (t.x==hero.x+dx and t.y==hero.y+dy)
                    ), None) if hero else None
                a1 = ActionMoveHero(hero_idx=0, dest=(hero.x+dx, hero.y+dy))
                if town and town.army and any(town.army):
                    a2 = ActionTransferArmy(src_town_idx=player.towns.index(town), dest_hero_idx=0, stack_idx=-1, amount=1000)
                    return [a1, a2]
                return a1
        elif self.action_end_turn == action:
            return ActionEndTurn()
        return None

class GameActionMapperOnlyMoveHero(GameActionMapper):
    MOVE_ACTION_DELTAS = [
        (-1,-1), (-1, 0), (-1,+1),
        ( 0,-1),          ( 0,+1),
        (+1,-1), (+1, 0), (+1,+1),
    ]
    MOVE_ACTION_NAMES = [
          'UpLeft',   'Up',   'UpRight',
            'Left',             'Right',
        'DownLeft', 'Down', 'DownRight',
    ]
    def __init__(self, env:HOMMGymEnv) -> None:
        # assert isinstance(env.observer, GameObserverMinimal)
        # obs_minimal:GameObserverMinimal = env.observer
        self.map_size = env.game.map.size
        env.game.autoskill_existing[env.ML_player_idx] = True

        self.total_actions_num = 0

        self.action_move_hero_start = self.total_actions_num
        self.total_actions_num += len(self.MOVE_ACTION_DELTAS)
        self.action_move_hero_end = self.total_actions_num-1

    def GetActionSpace(self, env:HOMMGymEnv) -> Space:
        return DiscreteMasked(self.total_actions_num)
    
    def GetValidActionsMask(self, env:HOMMGymEnv):
        env.game.autoskill_existing[env.ML_player_idx] = True # need to do this again due to successive reset()
        mask = np.ones(shape=(self.total_actions_num), dtype=bool)
        player = env.game.map.players[env.game.map.curr_player_idx]
        if len(player.heroes)>0:
            hero = player.heroes[0] # there is only one
            if hero.curr_movement <= 0:
                mask[self.action_move_hero_start:self.action_move_hero_end+1] = False
            for pos_idx in range(len(self.MOVE_ACTION_DELTAS)):
                dx,dy = self.MOVE_ACTION_DELTAS[pos_idx]
                x, y = hero.x+dx, hero.y+dy
                if not (env.game.map.IsInBounds(x, y) and env.game.map.ValidDestPos(x, y) and player.CanSee(x, y)
                        and hero.curr_movement >= env.game.map.Adj_Dist(hero.x, hero.y, x, y)):
                    mask[self.action_move_hero_start+pos_idx] = False
        discreteMasked:DiscreteMasked = env.action_space
        discreteMasked.UpdateMask(mask)
        return mask
    
    def UnmapAction(self, env:HOMMGymEnv, action) -> HOMMAction|list[HOMMAction]:
        # obs:GameObserverMinimal = env.observer
        # assert obs
        was_sampled = DiscreteMasked.SAMPLED
        DiscreteMasked.SAMPLED = False
        player = env.game.map.players[env.game.map.curr_player_idx] if not env.game.map.hero_leveling_up else env.game.map.players[env.game.map.hero_leveling_up.player_idx]
        if self.action_move_hero_start <= action <= self.action_move_hero_end:
            rest = action - self.action_move_hero_start
            dx,dy = self.MOVE_ACTION_DELTAS[rest]
            if len(player.heroes) > 0:
                hero = player.heroes[0] # there is only one
                town = next((t for t in player.towns
                    if (t.x==hero.x and t.y==hero.y) or (t.x==hero.x+dx and t.y==hero.y+dy)
                    ), None) if hero else None
                ret = []
                a = ActionMoveHero(hero_idx=0, dest=(hero.x+dx, hero.y+dy))
                a.agent_intent = self.MOVE_ACTION_NAMES[rest]
                if was_sampled:
                    a.agent_intent += ' sampled'
                ret.append(a)
                if town and town.army and any(town.army):
                    ret.append(ActionTransferArmy(src_town_idx=player.towns.index(town), dest_hero_idx=0, stack_idx=-1, amount=1000))
                if env.game.actions_this_turn >= env.game.max_actions_turn or hero.curr_movement < 100+141: # curr_movement < env.game.map.Adj_Dist(hero.x, hero.y, hero.x+dx, hero.y+dy)
                    ret.append(ActionEndTurn())
                return ret
            else:
                a = ActionRecruitHero(town_idx=0) # is this OK???
                a.is_forced = True
                return a
        return None

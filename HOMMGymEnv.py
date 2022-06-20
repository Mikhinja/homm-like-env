from typing import Callable, Optional, Union
from gym import Env, Space, spaces
from pyparsing import dictOf
import numpy as np

from HOMM.HOMMAPI import HOMMAI, HOMMAction, HOMMArmy, HOMMArmyStack, HOMMHero, HOMMMap, HOMMPlayer
from HOMM.HOMMActions import ActionBuild, ActionEndTurn, ActionMoveHero, ActionRecruitArmy, ActionRecruitHero, ActionSkillChoice, ActionTransferArmy
from HOMM.HOMMBuiltInAI_Procedural import DummyAI, PartialDummmyAI, ProceduralAI
from HOMM.HOMMData.HOMMHeroData import HeroSkills, HeroSpells
from HOMM.HOMMData.HOMMTownData import TownTypes
from HOMM.HOMMData.HOMMUnitData import UnitTypes

from HOMM.HOMMEnv import HOMMSimpleEnv
from HOMM.HOMMMap import HardcodedTemplate

# necessary for 
from HOMM.HOMMData.HOMMMapData import ResourcesConversionToGoldByIdx, TileTypesByName
from HOMM.Hero import Hero
from HOMM.Town import TownBase

_total_unit_types = len(UnitTypes) # len(UnitTypes) -- revisit this

class GameObserver(object):
    def GetSpace(self, env) -> Space:
        pass
    def GetObservation(self, env, last_action_was_accepted:bool=True, last_action_was_valid:bool=True):
        pass
    @staticmethod
    def GetObserver(obs_type:str):
        if obs_type == 'dict':
            from GameObserverDict import GameObserverDict
            return GameObserverDict()
        elif obs_type == 'selection':
            from GameObserverSelectionFlat import GameObserverSelectedHeroTown
            return GameObserverSelectedHeroTown()
        elif obs_type == 'selection-flat':
            from GameObserverSelectionFlat import GameObserverSelectedHeroTownFlat
            return GameObserverSelectedHeroTownFlat()
        elif obs_type == 'minimal':
            from GameObserverMinimal import GameObserverMinimal
            return GameObserverMinimal()
        elif obs_type == 'minimal-flat':
            from GameObserverMinimal import GameObserverMinimalFlat
            return GameObserverMinimalFlat()
        elif obs_type == 'really-minimal':
            from GameObserverMinimal import GameObserverReallyMinimal
            return GameObserverReallyMinimal()
        elif obs_type == 'really-minimal-flat':
            from GameObserverMinimal import GameObserverReallyMinimalFlat
            return GameObserverReallyMinimalFlat()

class GameActionMapper(object):
    def GetActionSpace(self, env) -> Space:
        pass
    def UnmapAction(self, env, action) -> HOMMAction|list[HOMMAction]:
        pass
    def GetValidActionsMask(self, env):
        pass
    @staticmethod
    def GetActionMapper(mapper_type:str, env):
        if mapper_type == 'big-flat':
            from GameObserverDict import GameActionMapperBigFlatSpace
            return GameActionMapperBigFlatSpace(env)
        elif mapper_type == 'selection':
            from GameObserverSelectionFlat import GameActionMapperSelection
            return GameActionMapperSelection(env)
        elif mapper_type == 'selection-reduced':
            from GameObserverSelectionFlat import GameActionMapperSelectionReduced
            return GameActionMapperSelectionReduced(env)
        elif mapper_type == 'minimal':
            from GameObserverMinimal import GameActionMapperMinimal
            return GameActionMapperMinimal(env)
        elif mapper_type == 'only-move':
            from GameObserverMinimal import GameActionMapperOnlyMoveHero
            return GameActionMapperOnlyMoveHero(env)

class HOMMGymEnv(Env):
    WIN_LOSS_REWARD = 10_000 # is this too high?
    REWARD_PER_HERO_LEVEL = 3 # is this a good idea?
    INVALID_ACTION_REWARD = -1
    UNACCEPTABLE_ACTION_REWARD_INCREMENT = -10 # should this be flat, or increment?

    # for debugging
    ACTIONS_THAT_WON = []
    ACTION_REWARDS = []
    TRAIN_STEP = 0
    
    def __init__(self, map_size:str='S', p2_use_procedural_ai:bool=True, p2_dummy_num:int=-1,
            max_heroes:int=1, allowed_actions_per_turn:int=50,
            observation_encoding:str='dict', action_mapper:str='big-flat', max_day='1:2:3',
            fixed_seed:Optional[int] = None) -> None:
        super().__init__()

        self.map_size = map_size
        self.fixed_seed = fixed_seed
        
        # TODO: make this playable by ML players without procedural AI
        self.ML_player_idx = 0
        self.max_heroes = max_heroes
        self.p2_use_procedural_ai = p2_use_procedural_ai
        self.p2_dummy_num = p2_dummy_num
        self.p2_ai:HOMMAI = None
        self.template = HardcodedTemplate(areas=2, size=self.map_size, max_day=max_day,
            max_heroes=self.max_heroes, allowed_actions_per_turn=allowed_actions_per_turn)
        self.game:HOMMSimpleEnv = None

        # ??? should the below be done by calling reset() here ?
        try:
            self.game = self.template.Generate()
        except:
            self.game = None
        if not self.game:
            self.game = self.template.Generate()
        assert self.game
        assert len(self.game.map.towns) <= 4, 'map template error: there are more than 4 towns in total, need to update the observation space as well'
        
        # add built-in AI, if any
        self.__set_procedural_ai__()

        # Start() will bring the game into a state where an action from the agent is expected
        self.game.Start()

        # useful for computing differential rewards
        self.prev_AIVals = [self.game.map.players[0].GetAIVal(), self.game.map.players[1].GetAIVal()]
        self.prev_Visibility = [np.count_nonzero(self.game.map.players[0].visibility), np.count_nonzero(self.game.map.players[1].visibility)]
        self.prev_SumHeroLevels = [1, 1] # start of game
        self.prev_SumResources = [self.__sum_resources__(self.game.map.players[0].resources), self.__sum_resources__(self.game.map.players[1].resources)]
        self.total_rewards = [0, 0]
        # also useful for discouraging invalid and unacceptable actions
        self.invalid_actions_since_last = 0
        self.unacceptable_actions_since_last = 0

        # TODO
        # compute observation space
        assert HOMMMap.MAX_PLAYER_HEROES == 4, 'max player heroes has changed, need to update the observation space as well'

        self.observation_encoding_name = observation_encoding
        self.observer = GameObserver.GetObserver(self.observation_encoding_name)
        self.observation_space = self.observer.GetSpace(self)
        
        # compute action space

        self.action_mapper_name = action_mapper
        self.action_mapper = GameActionMapper.GetActionMapper(mapper_type=action_mapper, env=self)
        self.action_space = self.action_mapper.GetActionSpace(self)
    
    def reset(self, *, seed: Optional[int] = None, return_info: bool = False, options: Optional[dict] = None):
        assert self.template
        assert self.observer
        assert self.action_mapper

        prev_reward = self.total_rewards[0]

        # set seed, or not ?
        # if RNG seed is changed, then should a new map be generated ?
        #   if not, then the map state should be reset (day=-1, clear actions, not ended, not started)
        # if RNG is not changed, then a new map should be generated
        if seed is not None:
            the_seed = seed
        else:
            the_seed = self.fixed_seed

        self.game = None
        if the_seed:
            try:
                self.game = self.template.Generate(seed=the_seed)
            except:
                pass
            if not self.game:
                self.game = self.template.Generate(seed=the_seed)
        else:
            try:
                self.game = self.template.Generate()
            except:
                pass
            if not self.game:
                self.game = self.template.Generate()

        # add built-in AI, if any
        self.__set_procedural_ai__()

        # start!
        self.game.Start()

        # useful for computing differential rewards
        self.prev_AIVals = [self.game.map.players[0].GetAIVal(), self.game.map.players[1].GetAIVal()]
        self.prev_Visibility = [np.count_nonzero(self.game.map.players[0].visibility), np.count_nonzero(self.game.map.players[1].visibility)]
        self.prev_SumHeroLevels = [1, 1] # start of game
        self.prev_SumResources = [self.__sum_resources__(self.game.map.players[0].resources), self.__sum_resources__(self.game.map.players[1].resources)]
        self.total_rewards = [0, 0]

        self.action_mapper.GetValidActionsMask(self) # hack to force updating the action space behind the scene
        self.ACTION_REWARDS.append(f'prev_reward={prev_reward}, step={self.TRAIN_STEP}   NEW GAME')

        obs = self.observer.GetObservation(self)

        return obs

    def __set_procedural_ai__(self):
        if self.p2_use_procedural_ai:
            if self.p2_dummy_num < 0:
                self.p2_ai = ProceduralAI(env=self.game, player=self.game.map.players[1])
            elif self.p2_dummy_num == 0:
                self.p2_ai = DummyAI(env=self.game, player=self.game.map.players[1])
            else:
                self.p2_ai = PartialDummmyAI(env=self.game, player=self.game.map.players[1], dummy_after_day=self.p2_dummy_num)

    def __do_game_actions__(self, homm_actions:list[HOMMAction]):
        was_valid = was_accepted = False
        for homm_action in homm_actions:
            self.game.DoAction(homm_action)
            was_accepted = was_accepted or homm_action.is_accepted
            was_valid = was_valid or homm_action.is_valid
        return was_accepted, was_valid

    def step(self, action):
        assert self.action_mapper
        homm_action = self.action_mapper.UnmapAction(env=self, action=action) #self.__unmap_action__(action=action)
        action_accepted = action_valid = False
        if homm_action:
            if isinstance(homm_action, list):
                action_accepted, action_valid = self.__do_game_actions__(homm_actions=homm_action)
            else:
                action_accepted, action_valid = self.__do_game_actions__(homm_actions=[homm_action])
                if not homm_action.is_for_game:
                    # hack for non-conventional actions
                    # is this still useful for anything?
                    is_valid = True
            # self.game.DoAction(homm_action)
            # action_valid = homm_action.is_valid
            # action_accepted = homm_action.is_accepted
            if not action_accepted:
                self.unacceptable_actions_since_last += 1
            elif not action_valid:
                self.invalid_actions_since_last += 1
            else:
                self.unacceptable_actions_since_last = self.invalid_actions_since_last = 0
        # hack to do some info from the training process
        if self.game.ended and self.ML_player_idx in self.game.winners:
            if isinstance(homm_action, list):
                self.ACTIONS_THAT_WON += homm_action
            else:
                self.ACTIONS_THAT_WON.append(homm_action)
        
        if homm_action:
            if isinstance(homm_action, list):
                turn_ended = next((True for a in homm_action if a.type=='end turn'), False)
            else:
                turn_ended = homm_action.type=='end turn'
        else:
            turn_ended = False
        
        reward = self.__compute_reward__(action_was_accepted=action_accepted,
            action_was_valid=action_valid,
            action_was_end_turn=turn_ended)
        
        # for investigating
        if isinstance(homm_action, list):
            self.ACTION_REWARDS.append(f'[day={self.game.map.day:>2}][=>{reward:>5.1f}] '+'\n\t\t\t\t '.join(f'{a} | {a.agent_intent}' for a in homm_action))
        else:
            self.ACTION_REWARDS.append(f'[day={self.game.map.day:>2}][=>{reward:>5.1f}] {homm_action} | {homm_action.agent_intent}')

        obs = self.observer.GetObservation(self)
        info = self.__get_info__()
        self.TRAIN_STEP += 1
        
        return obs, reward, self.game.ended, info
    
    def __get_info__(self) -> dict:
        assert self.game and self.game.started
        assert not self.game.map.battle

        return {
            'day': self.game.map.day,
            'current_player': self.game.map.curr_player_idx,
            'action': str(self.game.actions_log.Last()),
            'was_valid': self.game.actions_log.Last().is_valid if self.game.actions_log.Last() else False,
            'action_mask': self.action_mapper.GetValidActionsMask(env=self) # give some info about the valid action types
            # step_no
            # action -- as string, maybe?
            # reward -- again?
            # total_reward -- is this actually needed?
            # current_player?
            # is valid
        }
    
    @staticmethod
    def __log__(n:int):
        if n==0:
            return 0
        elif n<0:
            return -HOMMGymEnv.__log__(-n)
        return np.log(n)
    
    @staticmethod
    def __sum_resources__(res:list[int]) -> int:
        assert res or len(res) == 7
        return sum(res[idx] * ResourcesConversionToGoldByIdx[idx] for idx in range(7))
    
    def __compute_reward__(self, action_was_accepted:bool=True,
            action_was_valid:bool=True,
            action_was_end_turn:bool=False) -> float:
        # TODO: refactor this to work for all players (for self-play)
        assert self.ML_player_idx == self.game.map.curr_player_idx or self.game.ended or self.game.map.hero_leveling_up
        reward = 0
        if action_was_valid:
            player = self.game.map.players[self.ML_player_idx]
            other = self.game.map.players[self.ML_player_idx - 1]
            player_AIVal = player.GetAIVal()
            other_AIVal = other.GetAIVal()
            player_delta = player_AIVal - self.prev_AIVals[self.ML_player_idx]
            # we only consider other player's incremental actions during our own turn,
            #   otherwise it will mess up values of end-turn actions (when not forced)
            #   and of last action before forced end-turn action, whichever that may be
            other_delta = other_AIVal - self.prev_AIVals[self.ML_player_idx - 1] if not action_was_end_turn else 0
            players_visibility = [np.count_nonzero(self.game.map.players[0].visibility), np.count_nonzero(self.game.map.players[1].visibility)]
            #reward = player_AIVal + (player_delta - other_delta) if not self.game.ended else 0
            reward += self.__log__(player_delta//2)
            reward -= self.__log__(other_delta//2) if not self.game.ended else 0
            reward += 0.1 * (players_visibility[self.game.map.curr_player_idx]
                            - self.prev_Visibility[self.game.map.curr_player_idx])
            
            curr_SumHeroLevels = [sum(h.GetLevel() for h in self.game.map.players[0].heroes), sum(h.GetLevel() for h in self.game.map.players[1].heroes)]
            reward += self.REWARD_PER_HERO_LEVEL * (curr_SumHeroLevels[self.game.map.curr_player_idx] - self.prev_SumHeroLevels[self.game.map.curr_player_idx])
            curr_sum_res = self.__sum_resources__(self.game.map.players[0].resources)
            curr_sum_res /= 10 # should be less than army value, always
            if not action_was_end_turn:
                res_diff = curr_sum_res - self.prev_SumResources[0]
                if res_diff > 0: # is it ok to only consider resource gains, not spending?
                    reward += self.__log__(curr_sum_res - self.prev_SumResources[0])

            if self.game.ended:
                if player.IsDefeated():
                    reward -= self.WIN_LOSS_REWARD
                # if self.ML_player_idx in self.game.winners:
                #     reward += self.WIN_LOSS_REWARD
                if other.IsDefeated():
                    reward += self.WIN_LOSS_REWARD
            
            self.prev_AIVals = [player_AIVal, other_AIVal]
            self.prev_Visibility = players_visibility
            self.prev_SumHeroLevels = curr_SumHeroLevels
            self.prev_SumResources[0] = curr_sum_res
        elif action_was_accepted:
            reward = self.INVALID_ACTION_REWARD
        else:
            reward = self.UNACCEPTABLE_ACTION_REWARD_INCREMENT #* self.unacceptable_actions_since_last
        
        #reward += self.INVALID_ACTION_REWARD # is this a good idea?
        
        self.total_rewards[self.ML_player_idx] += reward
        return reward
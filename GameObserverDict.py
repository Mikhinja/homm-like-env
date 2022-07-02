from typing import OrderedDict
from gym import Space, spaces
from HOMMGymEnv import HOMMGymEnv, GameObserver, GameActionMapper
from HOMM.HOMMAPI import HOMMAction, HOMMArmyStack
from HOMM.HOMMActions import ActionBuild, ActionEndTurn, ActionMoveHero, ActionRecruitArmy, ActionRecruitHero, ActionSkillChoice, ActionTransferArmy
from HOMM.HOMMData.HOMMHeroData import HeroSkills, HeroSpells
from HOMM.HOMMData.HOMMMapData import TileTypesByName
from HOMM.HOMMData.HOMMTownData import TownTypes
from HOMM.HOMMData.HOMMUnitData import UnitTypes
from HOMM.Town import TownBase

_total_unit_types = len(UnitTypes) # len(UnitTypes) -- revisit this

class GameObserverDict(GameObserver):
    def GetSpace(self, env:HOMMGymEnv) -> Space:
        desc_dict = OrderedDict()
        # map tiles, offset by 1 because 0 will mean not visible to current player
        desc_dict['map'] = spaces.Box(low=0, high=1+len(TileTypesByName), shape=env.game.map.size)

        self.__get_hero_obs_desc__(env, desc_dict, 0)
        self.__get_hero_obs_desc__(env, desc_dict, 1)
        self.__get_hero_obs_desc__(env, desc_dict, 2)
        self.__get_hero_obs_desc__(env, desc_dict, 3)

        self.__get_hero_obs_desc__(env, desc_dict, 0, False)
        self.__get_hero_obs_desc__(env, desc_dict, 1, False)
        self.__get_hero_obs_desc__(env, desc_dict, 2, False)
        self.__get_hero_obs_desc__(env, desc_dict, 3, False)

        self.__get_town_obs_desc__(env, desc_dict, 0)
        self.__get_town_obs_desc__(env, desc_dict, 1)
        self.__get_town_obs_desc__(env, desc_dict, 2)
        self.__get_town_obs_desc__(env, desc_dict, 3)

        self.__get_town_obs_desc__(env, desc_dict, 0, False)
        self.__get_town_obs_desc__(env, desc_dict, 1, False)
        self.__get_town_obs_desc__(env, desc_dict, 2, False)
        self.__get_town_obs_desc__(env, desc_dict, 3, False)

        for idx in range(16):
            self.__get_neutral_army_obs_desc__(env, desc_dict, idx)

        return spaces.Dict(desc_dict)
    
    def GetObservation(self, env:HOMMGymEnv, last_action_was_accepted:bool=True, last_action_was_valid:bool=True):
        assert len(env.game.map.players) == 2
        player = env.game.map.players[env.game.map.curr_player_idx]
        #enemy = env.game.map.players[env.game.map.curr_player_idx - 1]
        other_towns = [t for t in env.game.map.towns if t.player_idx != player.idx]
        assert len(other_towns) <= 4
        assert len(env.game.map.neutral_armies) <= 16, 'template error: there are more than 16 neutral armies'

        dict_obs = OrderedDict()
        # map, masked by what is visible to current player
        dict_obs['map'] = (env.game.map.tiles[0,] + 1) * player.visibility.astype(int)
        
        self.__hero_obs__(env, dict_obs, 0)
        self.__hero_obs__(env, dict_obs, 1)
        self.__hero_obs__(env, dict_obs, 2)
        self.__hero_obs__(env, dict_obs, 3)

        self.__hero_obs__(env, dict_obs, 0, False)
        self.__hero_obs__(env, dict_obs, 1, False)
        self.__hero_obs__(env, dict_obs, 2, False)
        self.__hero_obs__(env, dict_obs, 3, False)

        self.__town_obs__(env, dict_obs, 0)
        self.__town_obs__(env, dict_obs, 1)
        self.__town_obs__(env, dict_obs, 2)
        self.__town_obs__(env, dict_obs, 3)

        self.__town_obs__(env, dict_obs, 0, False)
        self.__town_obs__(env, dict_obs, 1, False)
        self.__town_obs__(env, dict_obs, 2, False)
        self.__town_obs__(env, dict_obs, 3, False)

        for idx2 in range(16):
            self.__neutral_obs__(env, dict_obs, idx2)
       
        return dict_obs

    @staticmethod
    def __get_hero_obs_desc__(env:HOMMGymEnv, d:dict, idx:int, own:bool=True):
        d[f'{"own" if own else "enemy"} hero {idx} x'] = spaces.Discrete(env.game.map.size[0])
        d[f'{"own" if own else "enemy"} hero {idx} y'] = spaces.Discrete(env.game.map.size[1])
        d[f'{"own" if own else "enemy"} hero {idx} attack'] = spaces.Discrete(99)
        d[f'{"own" if own else "enemy"} hero {idx} defense'] = spaces.Discrete(99)
        d[f'{"own" if own else "enemy"} hero {idx} power'] = spaces.Discrete(99)
        d[f'{"own" if own else "enemy"} hero {idx} knowledge'] = spaces.Discrete(99)
        d[f'{"own" if own else "enemy"} hero {idx} current mana'] = spaces.Discrete(1000)
        d[f'{"own" if own else "enemy"} hero {idx} current movement'] = spaces.Discrete(4000)
        d[f'{"own" if own else "enemy"} hero {idx} skills'] = spaces.Box(low=0, high=3, shape=(len(HeroSkills),))
        d[f'{"own" if own else "enemy"} hero {idx} spells'] = spaces.MultiBinary(len(HeroSpells))
        for idx2 in range(7):
            d[f'{"own" if own else "enemy"} hero {idx} army stack {idx2} unit'] = spaces.Discrete(_total_unit_types)
            d[f'{"own" if own else "enemy"} hero {idx} army stack {idx2} amount'] = spaces.Discrete(HOMMArmyStack.MAX_IN_STACK)
    @staticmethod
    def __get_town_obs_desc__(env:HOMMGymEnv, d:dict, idx:int, own:bool=True):
        d[f'{"own" if own else "other"} town {idx} x'] = spaces.Discrete(env.game.map.size[0]+1)
        d[f'{"own" if own else "other"} town {idx} y'] = spaces.Discrete(env.game.map.size[1]+1)
        d[f'{"own" if own else "other"} town {idx} owner'] = spaces.Discrete(3)
        d[f'{"own" if own else "other"} town {idx} buildings'] = spaces.MultiBinary(len(TownTypes['Castle']['Buildings']))
        for idx2 in range(7):
            d[f'{"own" if own else "other"} town {idx} creature bank {idx2}'] = spaces.Discrete(1000)
        for idx2 in range(7):
            d[f'{"own" if own else "other"} town {idx} army stack {idx2} unit'] = spaces.Discrete(_total_unit_types)
            d[f'{"own" if own else "other"} town {idx} army stack {idx2} amount'] = spaces.Discrete(HOMMArmyStack.MAX_IN_STACK)
    @staticmethod
    def __get_neutral_army_obs_desc__(env:HOMMGymEnv, d:dict, idx:int):
        d[f'neutral {idx} x'] = spaces.Discrete(env.game.map.size[0])
        d[f'neutral {idx} y'] = spaces.Discrete(env.game.map.size[1])
        for idx2 in range(7):
            d[f'neutral {idx} army stack {idx2} unit'] = spaces.Discrete(_total_unit_types)
            d[f'neutral {idx} army stack {idx2} amount'] = spaces.Discrete(HOMMArmyStack.MAX_IN_STACK)
    
    @staticmethod
    def __hero_obs__(env:HOMMGymEnv, d:dict, idx:int, own:bool=True):
        player = env.game.map.players[env.game.map.curr_player_idx]
        enemy = env.game.map.players[env.game.map.curr_player_idx - 1]
        hero = None
        can_see = (own and len(player.heroes)>idx) or (not own and len(enemy.heroes)>idx and player.CanSee(enemy.heroes[idx].x, enemy.heroes[idx].y))
        if can_see:
            hero = player.heroes[idx] if own else enemy.heroes[idx]
        d[f'{"own" if own else "enemy"} hero {idx} x'] = hero.x if can_see else 0#-1
        d[f'{"own" if own else "enemy"} hero {idx} y'] = hero.y if can_see else 0#-1
        d[f'{"own" if own else "enemy"} hero {idx} attack'] = hero.attack if can_see else 0
        d[f'{"own" if own else "enemy"} hero {idx} defense'] = hero.defense if can_see else 0
        d[f'{"own" if own else "enemy"} hero {idx} power'] = hero.power if can_see else 0
        d[f'{"own" if own else "enemy"} hero {idx} knowledge'] = hero.knowledge if can_see else 0
        d[f'{"own" if own else "enemy"} hero {idx} current mana'] = hero.curr_mana if can_see else 0
        d[f'{"own" if own else "enemy"} hero {idx} current movement'] = hero.curr_movement if can_see else 0
        d[f'{"own" if own else "enemy"} hero {idx} skills'] = [hero.GetSkillLevel(skill_id) if can_see else 0 for skill_id in range(len(HeroSkills))]
        d[f'{"own" if own else "enemy"} hero {idx} spells'] = tuple([1 if can_see and spell_id in hero.spells else 0 for spell_id in range(len(HeroSpells))])
        for idx2 in range(7):
            stack = hero.army.stacks[idx2] if can_see and len(hero.army.stacks)>idx2 else None
            d[f'{"own" if own else "enemy"} hero {idx} army stack {idx2} unit'] = stack.unit_type if can_see and stack else 0
            d[f'{"own" if own else "enemy"} hero {idx} army stack {idx2} amount'] = stack.num if can_see and stack else 0
        return can_see
    @staticmethod
    def __town_obs__(env:HOMMGymEnv, d:dict, idx, own:bool=True):
        player = env.game.map.players[env.game.map.curr_player_idx]
        towns:list[TownBase] = player.towns if own else [t for t in env.game.map.towns if t.player_idx != player.idx]
        can_see = (own and len(player.towns)>idx) or (not own and len(towns)>idx and player.CanSee(towns[idx].x, towns[idx].y))
        town = towns[idx] if can_see else None
        d[f'{"own" if own else "other"} town {idx} x'] = town.x if can_see else 0#-1
        d[f'{"own" if own else "other"} town {idx} y'] = town.y if can_see else 0#-1
        d[f'{"own" if own else "other"} town {idx} owner'] = 1 + (town.player_idx if can_see else -1)
        d[f'{"own" if own else "other"} town {idx} buildings'] = [1 if can_see and building in town.buildings else 0 for building in TownTypes['Castle']['Buildings']]
        for idx2 in range(7):
            d[f'{"own" if own else "other"} town {idx} creature bank {idx2}'] = town.creature_bank[idx2] if can_see else 0
        for idx2 in range(7):
            stack = town.army.stacks[idx2] if can_see and town.army and len(town.army.stacks)>idx2 else None
            d[f'{"own" if own else "other"} town {idx} army stack {idx2} unit'] = stack.unit_type if can_see and stack else 0
            d[f'{"own" if own else "other"} town {idx} army stack {idx2} amount'] = stack.num if can_see and stack else 0
        return can_see
    @staticmethod
    def __neutral_obs__(env:HOMMGymEnv, d:dict, idx):
        player = env.game.map.players[env.game.map.curr_player_idx]
        neutral = env.game.map.neutral_armies[idx] if len(env.game.map.neutral_armies)>idx else None
        can_see = neutral and player.CanSee(neutral.x, neutral.y)
        d[f'neutral {idx} x'] = neutral.x if can_see else 0#-1
        d[f'neutral {idx} y'] = neutral.y if can_see else 0#-1
        for idx2 in range(7):
            stack = neutral.stacks[idx2] if can_see and len(neutral.stacks)>idx2 else None
            d[f'neutral {idx} army stack {idx2} unit'] = stack.unit_type if can_see and stack else 0
            d[f'neutral {idx} army stack {idx2} amount'] = stack.num if can_see and stack else 0
        return can_see

class GameActionMapperBigFlatSpace(GameActionMapper):
    def __init__(self, env:HOMMGymEnv) -> None:
        self.map_size = env.game.map.size

        #['ActionMoveHero', 'ActionBuild', 'ActionRecruitArmy', 'ActionTransferArmy', 'ActionRecruitHero', 'ActionSkillChoice', 'ActionEndTurn']
        self.action_types = [cls.__name__ for cls in HOMMAction.__subclasses__() if cls != 'BattleAction']
        
        self.total_actions_num = 0
        self.num_buildings_per_town = len(TownTypes['Castle']['Buildings'])

        # ActionBuild:          4 * num_buildings_per_town
        self.total_actions_num += 4 * self.num_buildings_per_town
        # ActionRecruitArmy:    4 * 14 because there are at most 4 towns, each has 14 units (7 levels + upgrades for each)
        self.action_recruit_army_start = self.total_actions_num
        self.total_actions_num += 4 * 14
        # ActionTransferArmy:   :
        #                       0-6         idx of stack, to simplify the amount will always be 1000, to default as maximum
        #                       0-2         town-to-hero=0, hero-to-town=1, hero-to-hero=2
        #                       0-3         idx of source
        #                       0-3         idx of dest
        self.action_transfer_army_start = self.total_actions_num
        self.total_actions_num += (7 * 3 * 4 * 4)
        # ActionRecruitHero:    4       idx of town in which to recruit hero
        self.actions_recruit_hero_start = self.total_actions_num
        self.total_actions_num += 4
        # ActionSkillChoice:    2       0=first choice, 1=second choice
        self.actions_skill_choice_start = self.total_actions_num
        self.total_actions_num += 2
        # ActionMoveHero:       4 * map size, one for each hero
        self.actions_move_hero_start = self.total_actions_num
        self.total_actions_num += 4 * env.game.map.size[0] * env.game.map.size[1]
        self.actions_end_turn = self.total_actions_num
        # ActionEndTurn:        1
        self.total_actions_num += 1

    def GetActionSpace(self, env:HOMMGymEnv) -> Space:
        return spaces.Discrete(self.total_actions_num)

    def UnmapAction(self, env:HOMMGymEnv, action) -> HOMMAction:
        assert env.game.map.size == self.map_size
        assert action >= 0 and action <= self.actions_end_turn
        # ActionBuild:          0 : self.action_recruit_army_start
        # ActionRecruitArmy:    self.action_recruit_army_start : self.action_transfer_army_start
        # ActionTransferArmy:   self.action_transfer_army_start : self.actions_recruit_hero_start
        #                       0-6         idx of stack, to simplify the amount will always be 1000, to default as maximum
        #                       0-2         town-to-hero=0, hero-to-town=1, hero-to-hero=2
        #                       0-3         idx of source
        #                       0-3         idx of dest
        # ActionRecruitHero:    self.actions_recruit_hero_start : self.actions_skill_choice_start
        # ActionSkillChoice:    self.actions_skill_choice_start : self.actions_move_hero_start
        # ActionMoveHero:       self.actions_move_hero_start : self.actions_end_turn
        # ActionEndTurn:        self.actions_end_turn
        if action < self.action_recruit_army_start:
            town_idx = action % 4
            building_idx = action // 4
            return ActionBuild(town_idx=town_idx, building_name=list(TownTypes['Castle']['Buildings'])[building_idx])
        elif self.action_recruit_army_start <= action < self.action_transfer_army_start:
            rest = action - self.action_recruit_army_start
            town_idx = rest % 4
            unit_type_idx = rest // 4
            unit_type_id = TownTypes['Castle']['Units'][unit_type_idx]
            return ActionRecruitArmy(town_idx=town_idx, unit_type=unit_type_id, amount=1000)
        elif self.action_transfer_army_start <= action < self.actions_recruit_hero_start:
            rest = action - self.action_transfer_army_start
            stack_idx = rest % 7
            rest = rest // 7
            transfer_type = rest % 3
            rest = rest // 3
            src_idx = rest % 4
            dest_idx = rest // 4
            if transfer_type == 0:
                # town to hero
                return ActionTransferArmy(stack_idx=stack_idx, amount=1000, src_town_idx=src_idx, dest_hero_idx=dest_idx)
            elif transfer_type == 1:
                # hero to town
                return ActionTransferArmy(stack_idx=stack_idx, amount=1000, src_hero_idx=src_idx, dest_town_idx=dest_idx)
            else:
                # hero to hero
                return ActionTransferArmy(stack_idx=stack_idx, amount=1000, src_hero_idx=src_idx, dest_hero_idx=dest_idx)
        elif self.actions_recruit_hero_start <= action < self.actions_skill_choice_start:
            rest = action - self.actions_recruit_hero_start
            return ActionRecruitHero(town_idx=rest)
        elif self.actions_skill_choice_start <= action < self.actions_move_hero_start:
            rest = action - self.actions_skill_choice_start
            return ActionSkillChoice(option=rest)
        elif self.actions_move_hero_start <= action < self.actions_end_turn:
            rest = action - self.actions_move_hero_start
            hero_idx = rest % 4
            rest = rest // 4
            x = rest % env.game.map.size[0]
            y = rest // env.game.map.size[0]
            return ActionMoveHero(hero_idx=hero_idx, dest=(x, y))
        elif action == self.actions_end_turn:
            return ActionEndTurn()
        return None

    def GetValidActionsMask(self, env:HOMMGymEnv):
        assert not env.game.map.battle # battle actions not yet supported
        if env.game.map.hero_leveling_up:
            valid_action_type_ids = [self.action_types.index('ActionSkillChoice')]
        else:
            valid_action_type_ids = [
                self.action_types.index('ActionMoveHero'),
                self.action_types.index('ActionBuild'),
                self.action_types.index('ActionRecruitArmy'),
                self.action_types.index('ActionTransferArmy'),
                self.action_types.index('ActionRecruitHero'),
                self.action_types.index('ActionEndTurn')
            ]
            player = env.game.map.players[env.game.map.curr_player_idx]
            if not player.heroes:
                valid_action_type_ids.remove(self.action_types.index('ActionMoveHero'))
                valid_action_type_ids.remove(self.action_types.index('ActionTransferArmy')) # transfer army between towns is not allowed
            if not player.towns:
                valid_action_type_ids.remove(self.action_types.index('ActionBuild'))
                valid_action_type_ids.remove(self.action_types.index('ActionRecruitArmy'))
                valid_action_type_ids.remove(self.action_types.index('ActionRecruitHero')) # can only recruit heroes in towns
        return valid_action_type_ids

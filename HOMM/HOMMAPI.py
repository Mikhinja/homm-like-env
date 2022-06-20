from argparse import Action, ArgumentError
from csv import excel
import math
from typing import Any, Callable, ClassVar
import numpy as np

from HOMM.HOMMData.HOMMHeroData import HeroLevelExperience, HeroSpells
from HOMM.HOMMData.HOMMArtifactsData import ART_CLASS_AI_VALS
from HOMM.HOMMData.HOMMMapData import MapObjTypeById, MapObjectTypes, MapResPileToIdx, TerrainTypes, TerrainTypesByName, TileTypes, TileTypesByName, TownTiles, can_step_on, is_valid_dest_tile
from HOMM.HOMMHeroes import HeroSkillUtils, HeroSpellUtils
from HOMM.HOMMUnitTypes import UnitUtils
#from Town import CastleTown
#import Army

class HOMMResourceObject(object):
    def __init__(self, res_type:int, value:int, pos:tuple[int, int]) -> None:
        self.res_type = res_type
        self.val = value
        self.pos = pos

class HOMMArmyStack(object):
    MAX_STACKS_IN_ARMY = 7
    MAX_IN_STACK = 1000 # TODO: implement this!
    # TODO: properly implement these too!
    SIZES = {
        0: (   0,    0), # INVALID
        1: (   1,    4), # few
        2: (   5,    9), # several
        3: (  10,   19), # pack
        4: (  20,   49), # lots
        5: (  50,   99), # horde
        6: ( 100,  249), # throng
        7: ( 250,  499), # swarm
        8: ( 500,  999), # zounds
        9: (1000, 4000)  # legion
    }
    def __init__(self, num:int, unit_id:int=None, unit_name:str=None):
        self.num = num
        if unit_id:
            self.unit_type = unit_id
        elif unit_name:
            self.unit_type = UnitUtils.GetUnitTypeByName(unit_name)
        else:
            raise ArgumentError('Neither unit_id nor unit_name was provided')
    def GetUnitType(self) -> int:
        return self.unit_type
    def GetUnitName(self) -> str:
        return UnitUtils.GetUnitName(self.unit_type)
    def GetUnitCount(self) -> int:
        return self.num
    def GetAIVal(self) -> int:
        return self.num * UnitUtils.GetAIValue(self.unit_type)
    def GetUnitSpeed(self):
        return UnitUtils.GetSpeed(self.unit_type)
    def GetAttack(self):
        return UnitUtils.GetAttack(self.unit_type)
    def GetDefense(self):
        return UnitUtils.GetDefense(self.unit_type)
    def GetDamage(self):
        return UnitUtils.GetDamage(self.unit_type)
    def GetAfflictions(self) -> list:
        # TODO 
        pass

class HOMMArmyIter(object):
    def __init__(self, army):
        self.parent = army
        self.idx = 0
    def __next__(self) -> HOMMArmyStack:
        curr_idx = self.idx
        self.idx += 1
        if curr_idx < HOMMArmyStack.MAX_STACKS_IN_ARMY and curr_idx < len(self.parent.stacks):
            return self.parent.GetStackAt(curr_idx)
        else:
            self.idx = 0
            raise StopIteration

class HOMMArmy(object):
    def __init__(self, stacks:list[HOMMArmyStack], x:int=None, y:int=None):
        self.stacks = stacks
        self.hero = None
        self.town = None
        if x is not None and y is not None:
            self.x=x
            self.y=y

    def GetStackAt(self, idx:int) -> HOMMArmyStack:
        if idx >= 0 and idx < len(self.stacks):
            return self.stacks[idx]
        return None
    def GetAIVal(self) -> int:
        return sum(stack.GetAIVal() for stack in self.stacks if stack.num > 0)
    def __iter__(self) -> HOMMArmyIter:
        return HOMMArmyIter(self)
    def CanCombine(self, other) -> bool:
        if other:
            all_unit_types = set([stack.unit_type for stack in self.stacks if stack.num>0] + [stack.unit_type for stack in other.stacks if stack.num>0])
            return len(all_unit_types) <= HOMMArmyStack.MAX_STACKS_IN_ARMY
        return False
    def Combine(self, other) -> bool:
        ok = self.CanCombine(other)
        if ok:
            i = 0
            while i < len(other.stacks):
                o_stack = other.stacks[i]
                my_stack = next((stack for stack in self.stacks if stack.unit_type == o_stack.unit_type), None)
                if my_stack:
                    my_stack.num += o_stack.num
                    o_stack.num = 0
                else:
                    self.stacks.append(o_stack)
                    other.stacks.remove(o_stack)
                    i -= 1
                i += 1
            i = 0
            while i < len(self.stacks):
                stack = self.stacks[i]
                if stack.num == 0:
                    self.stacks.remove(stack)
                    del stack
                    i -= 1
                i += 1
        return ok
    def TakeOne(self, other, idx:int, num:int=999) -> bool:
        if other and len(other.stacks) > idx:
            o_stack = other.stacks[idx]
            my_stack = next((stack for stack in self.stacks if stack.unit_type == o_stack.unit_type), None)
            if o_stack and o_stack.num > 0 and (my_stack or len([stack for stack in self.stacks if stack.num>0]) < HOMMArmyStack.MAX_STACKS_IN_ARMY):
                amount = min(num, o_stack.num)
                if my_stack:
                    my_stack.num += amount
                    o_stack.num -= amount
                else:
                    self.stacks.append(o_stack)
                    other.stacks.remove(o_stack)
                return True
        return False

class HOMMTown(object):
    def __init__(self, x:int, y:int, rng:np.random.RandomState) -> None:
        self.x = x
        self.y = y
        self.rng = rng
        # [0]=gold, [1]=wood, [2]=ore, [3]=mercuri, [4]=sulfur, [5]=crystal, [6]=gems
        self.income:list[int] = [0] * 7
        self.creature_bank:list[int] = [0] * 7
        self.creature_growth:list[int] = [0] * 7
        self.buildings:list[str] = []
        self.spells:list[int] = []
        self.player_idx:int = -1
        self.owner = None
        self.army:HOMMArmy = None
        self.built_today = False
    def GetAvailableToRecruit(self, level:int=None):
        if level:
            assert(level > 0 and level < 7)
            return self.creature_bank[level-1]
        return self.creature_bank
    def DayOver(self, newDayNum:int):
        pass
    def GetCostOfBuilding(self, building_name:str) -> list[int]:
        pass
    def Build(self, building_name:str) -> bool:
        pass
    def RecruitByLevel(self, amount: int, unit_lvl: int) -> bool:
        pass
    def Recruit(self, amount:int, unit_type:int) -> bool:
        pass
    def GetUnitTypeOfLevel(self, unit_lvl:int) -> int:
        pass
    def GetScoutingRadius(self) -> int:
        # TODO: implement modifiers for scouting radius: lookout tower, cover of darkness
        return 5

class HOMMHero(object):
    # TODO improve this system to add missing slots
    ARTEFACT_SLOTS = [
        'head',       # 0
        'cape',       # 1
        'neck',       # 2
        'weapon',     # 3
        'shield',     # 4
        'torso',      # 5
        'ring',       # 6
        'feet',       # 7
        'misc',       # 8
        'spell book', # 9 - TODO: implement having vs not having spell book
    ]
    MAX_SKILLS = 8
    def __init__(self, x:int, y:int, player_idx:int, rng:np.random.RandomState) -> None:
        self.x:int = x
        self.y:int = y
        self.player_idx = player_idx
        self.xp:int = 0
        self.attack:int = 0
        self.defense:int = 0
        self.power:int = 1 # cannot be 0
        self.knowledge:int = 1 # cannot be 0
        self.curr_mana:int = 10
        self.curr_movement:int = 1560 # this is the default for Castle (min speed 4)
        self.spells:list[int] = []
        self.skills:list[int] = []
        self.artifacts = [{}] * len(self.ARTEFACT_SLOTS)
        self.army:HOMMArmy = None # this is not valid, a hero cannot be without army
        self.map = None # TODO: fix (remove?) this dependency
        self.waiting_skill_choice = 0
    def DayOver(self, newDayNym:int):
        pass
    def GainXP(self, xp:int):
        pass
    def GetLevel(self) -> int:
        # levels are numbered starging from 1, so the implicit +1 from next() and > is just what we need here
        return next((i for i, x in enumerate(HeroLevelExperience) if x > self.xp), -1)
    
    def GetMaxMana(self) -> int:
        return int(10 * self.knowledge * (1 + self.GetSkillValue(HeroSkillUtils.GetSkillId('Intelligence'))))
    def GetBonus(self, what:str):
        return sum(a[what] for a in self.artifacts if what in a)
    def ReceiveResources(self, res:list):
        pass
    def Visit(self, town:HOMMTown):
        pass
    def ResetStartingArmy(self, give_starting_army:bool=True):
        pass
    def TakeArmyFrom(self, town:HOMMTown) -> bool:
        pass
    def GetSpellLevel(self, spell_id:int) -> int:
        pass
    def GetSpellCost(self, spell_id:int) -> int:
        pass
    def GetSpellValue(self, spell_id:int) -> int:
        pass
    def GetSkillLevel(self, skill_id:int) -> int:
        pass # not sure if this one is needed
    def GetSkillValue(self, skill_id:int):
        pass
    # TODO: implement retreat and surrender
    def Defeated(self):
        pass
    def GetSkillChoices(self) -> tuple[int,int]:
        pass
    def SkillLevelUp(self, skill_id:int) -> bool:
        pass
    def LearnSpell(self, spell_id:int) -> bool:
        pass
    def IsOnMap(self) -> bool:
        pass
    def GetScoutingRadius(self) -> int:
        # TODO: implement modifiers for scouting radius: scouting skill, artifacts
        return 5

class HOMMAction(object):
    ACTION_TYPES = ['build', 'move hero', 'recruit hero', 'recruit army', 'transfer army', 'map spell', 'battle action', 'skill choice', 'end turn', 'select', 'mock']
    ACTION_RESULTS = ['take resource', 'battle', 'levelup'] # TODO: add heroes army and artifacts transfer, and other events
    NewEndTurn:Callable = None
    def __init__(self, action_type:str='mock') -> None:
        assert(action_type in HOMMAction.ACTION_TYPES)
        self.type=action_type
        self.is_valid:bool=False
        self.is_accepted:bool=False
        self.is_for_game:bool=True
        self.is_from_proceduralAI=False

        self.player_idx:int=-1 # deduced from context when doing the action
        self.is_forced=False

        # for investigating what happened
        self.day:int=-1
        # TODO: revisit this at most 1 result per action paradigm
        self.result_what:str=None
        self.result:str=None
        self.result_where:tuple[int,int]=None
        self.dbg_info=''

        self.agent_intent = ''
    
    def ApplyAction(self, env) -> bool:
        self.day = env.map.day
        #assert self.player_idx >= 0 # actions can come from built-in AI for neutral armies (aka wandering monsters)
        return False # if not implemented, then always invalid
    
    def __str__(self) -> str:
        if self.player_idx >= 0:
            return f'[P{1+self.player_idx}] {self.type} {self.result_what} {self.result} {self.result_where} {self.dbg_info}'
        return f'[neutral] {self.type} {self.result_what} {self.result} {self.result_where}'

class HOMMActionLogger(object):
    callback:Callable
    def __init__(self) -> None:
        self.actions:list[HOMMAction] = []
        self.callback = None
    def LogAction(self, action:HOMMAction):
        self.actions.append(action)
        if self.callback:
            assert(callable(self.callback))
            self.callback()
    def Last(self) -> HOMMAction:
        if self.actions:
            return self.actions[-1]
        return None
    def Clear(self):
        self.actions.clear()


class HOMMAI(object):
    def __init__(self, env, player) -> None:
        pass
    def GetNextAction(self) -> HOMMAction:
        pass

class HOMMPlayer(object):
    def __init__(self, idx:int, map_size:tuple[int,int]) -> None:
        self.idx = idx
        self.towns:list[HOMMTown] = []
        self.heroes:list[HOMMHero] = []
        self.buildings = []
        self.days_to_get_town = 7
        # [0]=gold, [1]=wood, [2]=ore, [3]=mercuri, [4]=sulfur, [5]=crystal, [6]=gems
        self.resources:list[int] = [0] * 7
        self.map = None # useful for built-in AI, maybe
        self.ai:HOMMAI = None # TODO: revisit this
        self.visibility = np.zeros(map_size, dtype=bool)

        # recruiting heroes has a threshold each week, above that they will come with almost no army
        self.heroes_recruited_this_week = 0

        self.sel_hero_idx = 1 # starting hero, 0 = None (when no heroes are available)
        self.sel_town_idx = 1 # starting town, 0 = None (when no heroes are available)

    def DayOver(self, newDayNum:int) -> bool:
        if not self.IsDefeated():
            if not self.towns:
                self.days_to_get_town -= 1
            else:
                self.days_to_get_town = 7
                # for town in self.towns:
                #     town.DayOver(dayNum, self)
            for hero in self.heroes:
                hero.DayOver(newDayNum)
        if self.IsDefeated():
            self.Defeat()
        if 0 == newDayNum % 7:
            self.heroes_recruited_this_week = 0
        return self.IsDefeated()
    
    def Defeat(self):
        for hero in self.heroes:
            hero.Defeated()
        for town in self.towns:
            town.owner = None
            town.player_idx = -1

    @staticmethod
    def __inside_circle__(center:tuple[int,int], tile:tuple[int,int], radius:int) -> bool:
        dx = center[0] - tile[0]
        dy = center[1] - tile[1]
        return math.sqrt(dx**2 + dy**2) < radius
    
    def CanSee(self, x:int, y:int) -> bool:
        return self.visibility[x,y]
    
    def ScoutCircle(self, center:tuple[int,int], radius:int):
        for dx in range(-radius, radius):
            for dy in range(-radius, radius):
                pos = center[0]+dx, center[1]+dy
                if pos[0]>=0 and pos[0]<self.visibility.shape[0] and pos[1]>=0 and pos[1]<self.visibility.shape[1]:
                    if self.__inside_circle__(center, pos, radius):
                        self.visibility[pos[0],pos[1]] = True

    def TakeTown(self, town:HOMMTown) -> bool:
        if town.player_idx != self.idx:
            if town.player_idx >= 0:
                self.map.players[town.player_idx].towns.remove(town)
                self.map.players[town.player_idx].sel_town_idx = 1 if self.map.players[town.player_idx].towns else 0
            self.towns.append(town)
            town.player_idx = self.idx
            town.owner = self

            self.ScoutCircle((town.x, town.y), town.GetScoutingRadius())
            return True
        return False
    
    def ReceiveResources(self, res:list):
        assert(len(res) == 7 and len(self.resources) == 7)
        self.resources = [self.resources[i] + res[i] for i in range(7)]
    
    def CanAffort(self, cost:list[int]) -> bool:
        return all(self.resources[idx] >= cost[idx] for idx in range(7))
    def PayCost(self, cost:list[int]) -> bool:
        if self.CanAffort(cost):
            for idx in range(7):
                self.resources[idx] -= cost[idx]
            return True
        return False

    def IsDefeated(self) -> bool:
        return (not self.towns and not self.heroes) or (not self.towns and self.days_to_get_town <= 0)
    
    def GetAIVal(self) -> int:
        # TODO: treat defeated heroes, but not yet removed from map?
        ai_val = sum(hero.army.GetAIVal() for hero in self.heroes)
        ai_val += sum(sum(ART_CLASS_AI_VALS[art['class']] for art in hero.artifacts if art) for hero in self.heroes)

        ai_val += sum(town.army.GetAIVal() for town in self.towns if town.army)

        # TODO: maybe include something for resource and army income?

        return ai_val

# TODO link this to a hero
class HOMMArmyStackInCombat(object):
    def __init__(self, stack:HOMMArmyStack, orig_idx:int, x:int, y:int, hero:HOMMHero=None):
        self.stack = stack
        self.orig_idx = orig_idx
        self.health_left = UnitUtils.GetHealth(self.stack.GetUnitType())
        self.active_spells = self.GetNoSpellsList()
        self.curr_num = stack.num
        self.shots = UnitUtils.GetMaxShots(self.stack.unit_type)
        self.x = x
        self.y = y
        self.hero = hero
        self.prev_round = -1
        self.retaliated = False
        #self.speed = HeroUtils.GetArmyStackSpeed()
        #self.luck = 0 # TODO: get this based on hero attrib
        #self.morale = 0 # TODO: get this based on hero attrib
    def GetAIVal(self) -> int:
        return self.curr_num * UnitUtils.GetAIValue(self.stack.unit_type)
    def GetUnitSpeed(self, otherHero:HOMMHero):
        speed = self.stack.GetUnitSpeed()
        speed += self.hero.GetBonus('speed') if self.hero else 0
        # spell modifiers
        if self.active_spells[HeroSpellUtils.GetSpellId('haste')] > 0:
            speed += self.hero.GetSpellValue(HeroSpellUtils.GetSpellId('haste'))
        if self.active_spells[HeroSpellUtils.GetSpellId('prayer')] > 0:
            speed += self.hero.GetSpellValue(HeroSpellUtils.GetSpellId('prayer'))
        if self.active_spells[HeroSpellUtils.GetSpellId('slow')] > 0:
            if otherHero:
                val = otherHero.GetSpellValue(HeroSpellUtils.GetSpellId('slow'))
            else:
                val = HeroSpells[HeroSpellUtils.GetSpellId('slow')][1]
            speed *= 1 - val
        return speed
    
    def TakeDamage(self, damage:int):
        if damage < self.health_left:
            # take damage, but no units killed
            self.health_left -= damage
        else:
            damage -= self.health_left # remaining health
            self.curr_num -= 1
            killed = int(damage / UnitUtils.GetHealth(self.stack.unit_type))
            self.curr_num -= killed
            if self.curr_num > 0:
                damage -= killed * UnitUtils.GetHealth(self.stack.unit_type)
                self.health_left = UnitUtils.GetHealth(self.stack.unit_type) - damage
                assert(self.health_left > 0)
            else:
                self.curr_num = self.health_left = 0
    
    @staticmethod
    def GetNoSpellsList():
        return [0] * len(HeroSpells)

class HOMMArmyInCombatIter(object):
    def __init__(self, army):
        self.parent = army
        self.idx = 0
    def __next__(self) -> HOMMArmyStackInCombat:
        curr_idx = self.idx
        self.idx += 1
        if curr_idx < HOMMArmyStack.MAX_STACKS_IN_ARMY and curr_idx < len(self.parent.army):
            return self.parent.army[curr_idx]
        else:
            self.idx = 0
            raise StopIteration

class HOMMArmyInCombat(object):
    START_POS_LAYOUT = [ 'left', 'right', 'center', 'surround' ]
    def __init__(self, army:HOMMArmy, layout:str):
        if layout == 'surround':
            assert(len(stack for stack in army if stack) == 5)
            positions = [(0,0), (0,14), (5,14), (10,14), (10,0)]
        elif layout == 'center':
            positions = [(3,6), (3,8), (5,5), (5,7), (5,9), (7,6), (7,8)]
        elif layout == 'left':
            # TODO: adapt arrangement based on the number of stacks
            # TODO: tolerate 2-hex units
            positions = [(0,0), (2,0), (4,0), (5,0), (6,0), (8,0), (10,0)]
        elif layout == 'right':
            positions = [(0,14), (2,14), (4,14), (5,14), (6,14), (8,14), (10,14)]
        else:
            raise ArgumentError('Invalid army layout in combat')
        self.orig_army = army
        self.hero:HOMMHero = army.hero
        self.town:HOMMTown = army.town
        self.curr_mana:int = self.hero.curr_mana if self.hero else 0
        self.army = [HOMMArmyStackInCombat(stack, i, *positions[i], army.hero) for i, stack in enumerate(army) if stack]
    def GetAIVal(self) -> int:
        return sum(stack.GetAIVal() for stack in self.army if stack.curr_num > 0)
    def IsDefeated(self) -> bool:
        return not any(stack for stack in self.army if stack.curr_num > 0)
    def GetStackAt(self, idx:int) -> HOMMArmyStackInCombat:
        if idx >= 0 and idx < len(self.army):
            return self.army[idx]
        return None
    def __iter__(self) -> HOMMArmyInCombatIter:
        return HOMMArmyInCombatIter(self)



class HOMMBattlefield(object):
    # def FindPathTo(self, x1:int, y1:int, x2:int, y2:int) -> list:
    #     pass
    def StackPathTo(self, stack:HOMMArmyStackInCombat, dest:HOMMArmyStackInCombat) -> list:
        pass
    def GetClosestToTarget(self, stack:HOMMArmyStackInCombat, dest:HOMMArmyStackInCombat, otherHero:HOMMHero) -> tuple[int, int]:
        pass
    def AreNeighbors(self, source:tuple[int,int], dest:tuple[int,int]) -> bool:
        pass

class HOMMAutoCombatAI(object):
    def __init__(self) -> None:
        pass
    # TODO: refactor this to return HOMMAction
    def GetNextBattleAction(self, currArmy:HOMMArmyInCombat, currStackIdx:int, otherArmy:HOMMArmyInCombat,
            battlefield:HOMMBattlefield, spellAllowed:bool=False) -> HOMMAction:
        pass

class HOMMBattle(object):
    BATTLE_LAYOUT = ['normal', 'ambush']
    def __init__(self, heroA:HOMMHero, armyD:HOMMArmy, layout:str, rng:np.random.RandomState) -> None:
        self.heroA = heroA
        self.orig_armyD = armyD
        self.armyA:HOMMArmyInCombat = None
        self.armyD:HOMMArmyInCombat = None
        self.ai:HOMMAutoCombatAI = None
        self.curr_stack:HOMMArmyStackInCombat = None
        self.prev_stack:HOMMArmyStackInCombat = None # useful for rendering, and nothing else??
        self.attacker_action = False
        self.actions_log:HOMMActionLogger = None
        self.attacker_won = False # default (maximum rounds expire, attacker loses by default)
    def GetCurrentStack(self):
        return self.attacker_action, self.curr_stack
    def AutoCombat(self, action_log:HOMMActionLogger=None):
        pass
    def GetResult(self) -> tuple:
        pass
    def Reset(self):
        pass
    # not sure how this should work
    def ApplyResult(self, the_map) -> bool:
        pass
    # TODO: refactor this to work with HOMMAction
    # not sure about this one, if/how it should work
    def DoAction(self, action=None) -> bool:
        pass
    def NewRound(self):
        pass
    def IsBattleOver(self) -> bool:
        pass
class HOMMBattleFactory(object):
    def __init__(self) -> None:
        pass
    def NewBattle(self, heroA:HOMMHero, armyD:HOMMArmy, layout:str) -> HOMMBattle:
        pass


class HOMMMap(object):
    MAX_PLAYER_HEROES = 4
    # Maximum number of towns is 48 on any map. According to https://heroes.thelazy.net/index.php/Town
    # we will use a smaller number
    MAX_TOWNS = 8
    MAX_OBSTACLES = 256
    MAX_NEUTRALS = 16
    MAX_RESOURCES = 64 # is this actually used?
    def __init__(self, num_players:int, size:tuple[int,int], template=None):
        self.size = size
        self.fixed_obstacles = [] # TODO: rethink this
        #self.move_tiles = np
        self.tiles = np.zeros((3, *self.size), order='F', dtype=int)
        self.tiles[1,:,:] = 1 # set everything to grass by default
        assert(num_players>0)
        self.players:list[HOMMPlayer] = [HOMMPlayer(idx=i, map_size=self.size) for i in range(num_players)] # should this be here? or should it only be in env?
        self.towns:list[HOMMTown] = []
        self.heroes:list[HOMMHero] = [] # should this be here? or should it only be in env?
        self.neutral_armies:list[HOMMArmy] = []
        self.resources2:list[HOMMResourceObject] = [] # source of truth
        self.resources:dict[(int, int): HOMMResourceObject] = {} # optimization - TODO: improve this
        self.day = -1
        self.curr_player_idx = 0
        self.battle:HOMMBattle = None # TODO: move this out of here and into the env, send it through the action object
        self.hero_leveling_up:HOMMHero = None
        self.day_over_callback = None
        # optimization for A*
        self._cache_astar = True
        self.__gScoresCache = {}
        self.__came_from_cache = {}

    def GetTownAt(self, x:int, y:int) -> HOMMTown:
        return next((t for t in self.towns if t.x == x and t.y == y), None)
    def AddTown(self, new_town:HOMMTown) -> bool:
        assert(len(self.towns) < HOMMMap.MAX_TOWNS)
        ok = all(can_step_on(self.tiles[0, new_town.x+x, new_town.y+y]) for x,y in TownTiles)
        if ok:
            for dx,dy in TownTiles:
                self.tiles[0, new_town.x+dx, new_town.y+dy] = TileTypesByName['wall']
                # TODO change this to be more generic, or move it from here
            self.tiles[2, new_town.x, new_town.y] = MapObjectTypes['Castle Town']['id']
            self.towns.append(new_town)
        return ok
    def AddHero(self, new_hero:HOMMHero) -> bool:
        #ok = can_step_on(self.tiles[0, new_hero.x, new_hero.y])
        ok = self.CanStepOn(new_hero, new_hero.x, new_hero.y) or new_hero.player_idx == -1
        if ok:
            if new_hero not in self.heroes:
                self.heroes.append(new_hero)
                new_hero.map = self
            if new_hero.player_idx >= 0:
                self.GiveHeroTo(new_hero, self.players[new_hero.player_idx])
        return ok
    def GiveHeroTo(self, hero:HOMMHero, player:HOMMPlayer, pos:tuple[int,int]) -> bool:
        assert(hero in self.heroes and player in self.players)
        assert hero and player, 'can not give either no hero or to no player'
        if self.CanStepOn(hero, *pos) and hero not in player.heroes and len(player.heroes) < HOMMMap.MAX_PLAYER_HEROES:
            hero.x = pos[0]
            hero.y = pos[1]
            self.tiles[0, hero.x, hero.y] = TileTypesByName['hero or army']
            player.heroes.append(hero)
            hero.player_idx = player.idx
            hero.owner = player
            return True
        return False
    def AddResource(self, x:int, y:int, res_type:int, res_val:int) -> bool:
        assert len(self.resources) <= HOMMMap.MAX_RESOURCES
        ok = self.tiles[0, x, y] == 0
        if ok:
            self.tiles[0, x, y] = TileTypesByName['resource']
            self.tiles[2, x, y] = res_type
            res = HOMMResourceObject(res_type, res_val, (x, y))
            self.resources2.append(res)
            # self.resources[(x, y)] = (res_type, res_val)
            self.resources[(x, y)] = res
        return ok
    def AddNeutralArmy(self, army:HOMMArmy) -> bool:
        assert army, 'Error adding army: army can not be None'
        assert len(self.neutral_armies) <= HOMMMap.MAX_NEUTRALS
        assert self.IsInBounds(army.x, army.y), 'Error adding army: army outside map'
        assert can_step_on(self.tiles[0, army.x, army.y]), f'Error adding army: invalid position {(army.x, army.y)} because {TileTypes[self.tiles[0, army.x, army.y]]["name"]}'
        self.tiles[0, army.x, army.y] = TileTypesByName['hero or army']
        self.neutral_armies.append(army)
        return True
    def RemoveNeutralArmy(self, army:HOMMArmy) -> bool:
        try:
            self.neutral_armies.remove(army)
            self.tiles[0, army.x, army.y] = TileTypesByName['free']
            return True
        except:
            return False
    def TakeResource(self, x:int, y:int) -> list:
        pos = x,y
        # what_res, how_much = self.resources[pos]
        res:HOMMResourceObject = self.resources[pos]
        one_of_7_res = [0] * 7
        if MapObjTypeById[res.res_type].casefold() == 'Treasure Chest'.casefold():
            one_of_7_res[0] = 500 + res.val # gold
            one_of_7_res.append(res.val) # xp
        else:
            one_of_7_res[MapResPileToIdx[res.res_type]] = res.val
        self.tiles[0, pos[0],pos[1]] = TileTypesByName['free']
        self.tiles[2, pos[0],pos[1]] = 0
        self.resources2.remove(res)
        del self.resources[pos]
        del res # do not do this for artifacts
        return one_of_7_res
    
    def AddRoad(self, path:list[tuple[int,int]], road_type:str='Dirt road'):
        assert path, 'Error: road path cannot be None'
        road_type_id = TerrainTypesByName[road_type]
        for pos in path:
            x,y = pos
            assert can_step_on(self.tiles[0,x,y]), 'Error: invalid road path!'
            self.tiles[0,x,y] = TileTypesByName['road']
            self.tiles[1,x,y] = road_type_id

    def DayOver(self):
        self.day += 1
        for player in self.players:
            player.DayOver(self.day)
        for town in self.towns:
            town.DayOver(self.day)
        if self.day_over_callback:
            self.day_over_callback(self.day)
    
    def GetDayStr(self) -> str:
        return f'{1+int(int(self.day/7)/4)}:{1+int(self.day/7)}:{1+int(self.day%7)}'
    @staticmethod
    def DayToStr(day_num:int) -> str:
        return f'{1+int(int(day_num/7)/4)}:{1+int(day_num/7)}:{1+int(day_num%7)}'
    @staticmethod
    def DayFromStr(day_str:str) -> int:
        vals = day_str.split(':')
        assert(len(vals)==3)
        return ((int(vals[0])-1)*4 + (int(vals[1])-1))*7 + int(vals[2])-1
    
    def EndTurn(self) -> bool:
        ret = False
        self.curr_player_idx += 1
        if self.curr_player_idx >= len(self.players):
            self.curr_player_idx = 0
            self.DayOver()
            ret = True
        
        # automatic end turns for defeated players
        if self.players[self.curr_player_idx].IsDefeated():
            assert(sum(1 for p in self.players if not p.IsDefeated()) > 0)
            self.EndTurn()
        
        return ret

    def IsInBounds(self, x:int, y:int) -> bool:
        return x>=0 and y>=0 and x < self.tiles.shape[1] and y < self.tiles.shape[2]
    def ValidDestPos(self, x:int, y:int) -> bool:
        return self.IsInBounds(x, y) and is_valid_dest_tile(self.tiles[0, x, y])
    def CanStepOn(self, hero:HOMMHero, x:int, y:int) -> bool:
        assert(hero) # and hero.player_idx >= 0
        if self.IsInBounds(x, y):
            if can_step_on(self.tiles[0,x,y]):
                town = self.GetTownAt(x, y)
                if town:
                    if town.player_idx < 0 and not (town.army and any(town.army)):
                        return True
                    # hero.player_idx could be -1 when giving a hero to a player
                    elif town.player_idx == hero.player_idx or hero.player_idx == -1 or not (town.army and any(town.army)):
                        return True
                else:
                    return True
                #return can_step_on(self.tiles[0,x,y]) if self.__is_in_bounds__(x, y) else False
        return False
    def MovementFactorAt(self, x:int, y:int) -> float:
        return TerrainTypes[self.tiles[1, x, y]]['factor']
    def Adj_Dist(self, x1:int, y1:int, x2:int, y2:int) -> int:
        if x1!=x2 or y1!=y2:
            assert(abs(x2-x1) <= 1 and abs(y2-y1) <= 1)
            if abs(x2-x1) == 1 and abs(y2-y1) == 1:
                return int(141 * self.MovementFactorAt(x1, y1))
            else:
                return int(100 * self.MovementFactorAt(x1, y1))
        return 0
    @staticmethod
    def __are_neighbors__(x1:int, y1:int, x2:int, y2:int):
        return abs(x2-x1) <= 1 and abs(y2-y1) <= 1
    
    __NEIGH_DIFF = [
        (-1,-1), (-1, 0), (-1, 1),
        ( 0,-1),          ( 0, 1),
        ( 1,-1), ( 1, 0), ( 1, 1),
    ]
    def __neighbors__(self, hero:HOMMHero, x:int, y:int) -> list[tuple[int,int]]:
        return [(x+dx, y+dy) for dx,dy in self.__NEIGH_DIFF if self.CanStepOn(hero, x+dx, y+dy)]
    def __h__(self, pos:tuple, end:tuple) -> int: # based on Mahattan distance
        return int(100 * self.MovementFactorAt(*pos) * (abs(end[0] - pos[0]) + abs(end[1] - pos[1])))
    def FindPathTo(self, hero:HOMMHero, dest_x, dest_y, ignore_visibility:bool=False) -> list:
        if not ignore_visibility and hero.player_idx>=0 and not self.players[hero.player_idx].CanSee(dest_x, dest_y):
            return False
        if is_valid_dest_tile(self.tiles[0, dest_x, dest_y]):
            dest_is_free = self.CanStepOn(hero, dest_x, dest_y)
            start = (hero.x, hero.y)
            end = (dest_x, dest_y)
            open_set = [start]
            fScore = { start: self.__h__(start, end) }
            gScore, came_from = self.__get_cached_gScores__(hero)
            if gScore:
                if end in came_from:
                    # cache fully hit, this happens when a previous path search looked farther than this
                    curr = end
                    path = [] #[curr]
                    while curr in came_from and curr != start:
                        path.append(curr)
                        curr = came_from[curr]
                    path.reverse()
                    if not path or path[-1] != end:
                        path.append(end) # this is needed in order to pick up resources, since that requires a false step
                    return path
                else:
                    # we have not had a full hit, only a partial hit, which means the search continues
                    # we gain an advantage by starting from the boundary of what we explored previously
                    # but because previous searches looked farther they might have ignored our target,
                    #   so we need to make sure we do not exclude the neighbors of our destination
                    open_set += list(set(came_from) - (set(came_from.values()) - set(self.__neighbors__(hero, *end))))
                    # we also need to recalculate the fScore for the boundary
                    # the fScores are different since the destination is different
                    # note: we need to have the fScore for the starting position since the new direction might not be explored at all
                    for pos in open_set:
                        fScore[pos] = gScore[pos] + self.__h__(pos, end)
            else:
                came_from = {}
                gScore = { start: 0 }

            while open_set:
                curr = min(open_set, key=lambda x:fScore[x] if x in fScore else gScore[x] + self.__h__(x, end))
                # if the destination is a resource or other army, we can stop at an adjacent position
                if curr == end or (not dest_is_free and self.__are_neighbors__(*curr, *end)):
                    path = [] #[curr]
                    while curr in came_from and curr != start:
                        path.append(curr)
                        curr = came_from[curr]
                    path.reverse()
                    if not path or path[-1] != end:
                        path.append(end) # this is needed in order to pick up resources, since that requires a false step
                    if self._cache_astar:
                        # NOTE TO SELF: do NOT add non-free destinations to cache, because they break pathing since they
                        #               allow traversing positions that can't normally be passed over!
                        # if not dest_is_free and len(path)>1:
                        #     came_from[path[-1]] = path[-2]
                        #     gScore[path[-1]] = gScore[path[-2]] + self.__adj_dist__(*path[-1], *path[-2])
                        self.__cache_gScores__(hero, gScores=gScore, came_from=came_from)
                    return path
                open_set.remove(curr)
                for neigh in self.__neighbors__(hero, *curr):
                    tentative_g_score = gScore.get(curr, math.inf) + self.Adj_Dist(*curr, *neigh)
                    if tentative_g_score < gScore.get(neigh, math.inf):
                        came_from[neigh] = curr
                        gScore[neigh] = tentative_g_score
                        fScore[neigh] = tentative_g_score + self.__h__(neigh, end)
                        if neigh not in open_set:
                            open_set.append(neigh)

        return False
    def __cache_gScores__(self, hero:HOMMHero, gScores:dict, came_from:dict):
        # do not cache non-player heroes (used for map generation)
        if hero.player_idx >= 0:
            key = (hero.player_idx, hero.x, hero.y)
            self.__gScoresCache[key] = gScores
            self.__came_from_cache[key] = came_from
    def __get_cached_gScores__(self, hero:HOMMHero) :#-> tuple[dict, dict] | tuple[None, None]:
        key = (hero.player_idx, hero.x, hero.y)
        if key in self.__gScoresCache:
            return self.__gScoresCache[key], self.__came_from_cache[key]
        return None, None
    def Clear_Cached_gScores(self, hero:HOMMHero=None):
        if hero:
            key = (hero.player_idx, hero.x, hero.y)
            if key in self.__gScoresCache:
                del self.__gScoresCache[key]
                del self.__came_from_cache[key]
        else:
            self.__gScoresCache.clear()
            self.__came_from_cache.clear()


class HOMMRenderer(object):
    def __init__(self, env, actions_log:HOMMActionLogger, num_actions:int=3,
                    frame_delay:float=0.5,
                    record_animation:bool=False, animation_frame_delay:float=0.3, animation_filename:str='HOMMAnimation') -> None:
        self.num_actions = num_actions
        self.env = env
        self.frame_delay = frame_delay if frame_delay > 0 else 0.2
        self.record_animation = record_animation
        self.animation_frame_delay = animation_frame_delay
        self.animation_filename = animation_filename
    def CallBack(self):
        pass
    def SaveAnimation(self, specific_filename:str=None):
        pass
    def GameEnded(self):
        pass
    def Playback(self):
        pass


#from copyreg import pickle
# import json
# import pickle
import jsonpickle
from numpy.random import MT19937
from numpy.random import RandomState, SeedSequence
# from tkinter.tix import Tree
from HOMM.HOMMAPI import HOMMActionLogger, HOMMArmy, HOMMArmyStack, HOMMHero, HOMMPlayer, HOMMMap, HOMMAction, HOMMRenderer
from HOMM.HOMMData.HOMMHeroData import HeroDefinitions, HeroSkills
from HOMM.HOMMHeroes import HeroSkillUtils
from HOMM.HOMMRenderer import HOMMColorTextConsoleRender
from HOMM.HOMMUnitTypes import UnitUtils
from HOMM.Hero import Hero

# for serializing and deserializing
from ast import literal_eval


class HOMMSimpleEnv:
    # TODO: add templates
    # TODO: implement victory condition
    STARTING_RESOURCES_EASY       = [30000, 30, 30, 15, 15, 15, 15]
    STARTING_RESOURCES_NORMAL     = [20000, 20, 20, 10, 10, 10, 10]
    STARTING_RESOURCES_HARD       = [15000, 15, 15,  7,  7,  7,  7]
    STARTING_RESOURCES_EXPERT     = [10000, 10, 10,  4,  4,  4,  4]
    STARTING_RESOURCES_IMPOSSIBLE = [    0,  0,  0,  0,  0,  0,  0]
    def __init__(self, map_size:tuple=(36,36), num_players:int=2, only_autocombat:bool=True, renderer:str=None,
            starting_resources:list[int]=STARTING_RESOURCES_EXPERT, max_actions_turn:int=50,
            max_day:str='9:4:7', last_player_win:bool=True, strongest_army_win:bool=True, seed:int=None):
        assert(num_players >= 2) # TODO: allow 1 player?
        #self.Players = [HOMMPlayer(i, self) for i in range(num_players)]
        self.actions_log = HOMMActionLogger()
        self.num_players = num_players
        self.map_size = map_size
        self.only_autocombat = only_autocombat

        # for randomeness repeatability
        if seed:
            self.rng = MT19937(SeedSequence(seed))
        else:
            self.rng = MT19937()
        self.rs = RandomState(self.rng)
        self.rng_start_state = self.rs.get_state()
        self.rng_state = self.rng_start_state
        self.rng.state = self.rng_state
        self.started = False

        self.map = HOMMMap(num_players=num_players, size=map_size)
        for player in self.map.players:
            player.map = self.map
            player.ReceiveResources(starting_resources)
        for hero_name in HeroDefinitions:
            self.map.AddHero(Hero(x=-1, y=-1, player_idx=-1, rng=self.rs, hero_def_name=hero_name))
        
        self.renderer:HOMMRenderer = None
        self.SetRenderer(renderer=renderer)

        self.autoskill_existing = [False] * self.num_players

        self.starting_resources = starting_resources
        self.max_day = HOMMMap.DayFromStr(max_day)
        self.max_actions_turn = max_actions_turn
        self.actions_this_turn = 0
        self.ended = False
        self.last_player_win = last_player_win
        self.strongest_army_win = strongest_army_win
        self.winners = []

        # useful to replay
        self.curr_day_state:str = None
        self.prev_day_state:str = None
        self.start_state:str = None
        
        # useful for debug...
        # transient values, should NOT be saved
        self.auto_playing_builtin_ai = False
        self.interrupt_daily = False
        self.interrupt_after_each_action = False
        self.reload_curr_day = False
        self.reload_prev_day = False
        self.prev_action_str = None
        self.check_same_action_in_succession = False
    
    def SetRenderer(self, renderer:str=None):
        if self.renderer:
            del self.renderer
        if renderer == 'colortext':
            self.renderer = HOMMColorTextConsoleRender(self.map, actions_log=self.actions_log)
            self.renderer.env = self
    
    def CheckVictory(self) -> bool:
        if not self.ended:
            if self.last_player_win:
                if 1 == sum(1 for i in range(len(self.map.players)) if not self.map.players[i].IsDefeated()):
                    self.winners = [next(player for player in self.map.players if not player.IsDefeated())]
                    self.__end__()
            
            if not self.ended and self.map.day > self.max_day:
                if self.strongest_army_win:
                    self.winners = [max((player for player in self.map.players), key=lambda p: p.GetAIVal())]
                    self.__end__()
                else:
                    self.winners = [player for player in self.map.players if not player.IsDefeated()]
                    self.__end__()
    
    def __end__(self):
        assert(self.started)
        self.ended = True
        if self.renderer:
            self.renderer.GameEnded()
            #self.renderer.SaveAnimation()

    def SaveState(self) -> str:
        self.rng_state = self.rs.get_state()
        pickle_json = jsonpickle.encode([self.map,
            self.actions_log.actions,
            self.started,
            self.ended,
            self.only_autocombat,
            self.map_size,
            self.num_players,
            self.rng_start_state,
            self.rng_state,
            self.interrupt_daily,
            self.interrupt_after_each_action], indent=2)
        return pickle_json

    def LoadState(self, pickle_json:str) -> bool:
        assert(pickle_json)
        #assert(not self.auto_playing_builtin_ai)
        parts = jsonpickle.decode(pickle_json)
        self.map = parts[0]
        str_keys = [k for k in self.map.resources.keys()]
        for str_key in str_keys:
            tpl = eval(str_key)
            self.map.resources[tpl] = self.map.resources[str_key]
            del self.map.resources[str_key]
        self.actions_log.actions = parts[1]
        self.started = parts[2]
        self.ended = parts[3]
        self.only_autocombat = parts[4]
        self.map_size = parts[5]
        self.num_players = parts[6]
        self.rng_start_state = parts[7]
        self.rng_state = parts[8]
        self.interrupt_daily = parts[9]
        self.interrupt_after_each_action = parts[10]
        self.rng.state = self.rng_state # is this needed?
        self.rs.set_state(self.rng.state)
        #assert(not self.auto_playing_builtin_ai)
        
        # TODO: uncomment this when not debugging
        # if self.started:
        #     # this is needed to avoid a state where a built-in AI needs to perform actions after load
        #     self.ContinueAuto()
        
        return True

    def IsBattleOngoing(self) -> bool:
        return self.map.battle is not None

    def Start(self):
        assert(not self.started and self.map.day == -1 and not self.ended)
        #self.rs.set_state(self.rng_start_state)
        self.start_state = self.SaveState()
        self.LoadState(self.start_state)
        self.started = True
        self.map.DayOver()
        self.DayOver()
        self.ContinueAuto()
    
    def DayOver(self):
        self.prev_day_state = self.curr_day_state
        self.curr_day_state = self.SaveState()
        # TODO: find a better way to insert a "frame" with the adventure map after a day is over
        if self.actions_log.callback and not self.ended:
            self.actions_log.callback(True)

    def ContinueAuto(self):
        if not self.auto_playing_builtin_ai: # prevent recursion
            player = self.map.players[self.map.curr_player_idx] if not self.map.hero_leveling_up else self.map.players[self.map.hero_leveling_up.player_idx]
            self.auto_playing_builtin_ai = True
            while player.ai and not self.ended:
                # if self.map.hero_leveling_up:
                #     player = self.map.players[self.map.hero_leveling_up.player_idx]
                #     if not player.ai:
                #         # give action to player that has the hero to level up
                #         break
                day_num_1 = self.map.day
                self.DoAction(player.ai.GetNextAction())
                day_num_2 = self.map.day
                if self.interrupt_after_each_action or (self.interrupt_daily and day_num_1 < day_num_2):
                    break
                # need to always get the current player since after one action a battle could have resulted in oponnent hero leveling up
                player = self.map.players[self.map.curr_player_idx] if not self.map.hero_leveling_up else self.map.players[self.map.hero_leveling_up.player_idx]
            self.auto_playing_builtin_ai = False
    
    def AcceptAction(self, action:HOMMAction) -> bool:
        if action.is_for_game:
            if self.IsBattleOngoing():
                return action.type == 'battle action'
            elif self.map.hero_leveling_up:
                return action.type == 'skill choice'
            else:
                return action.type in HOMMAction.ACTION_TYPES
        return False

    def DoAction(self, action:HOMMAction) -> bool:
        assert(action)
        if self.ended:
            action.is_accepted = action.is_valid = False
            return False
        # TODO: refactor battle actions also
        if self.map.hero_leveling_up:
            action.dbg_info = f'hero of P{1+self.map.hero_leveling_up.player_idx} waiting levelup'
        if self.IsBattleOngoing():
            if action.type == 'battle action':
                if not self.map.battle.IsBattleOver():
                    action.is_valid = self.map.battle.DoAction(action)
                
                if not self.map.battle.IsBattleOver():
                    # TODO: revisit this the level-up implementation
                    level_up = self.map.battle.ApplyResult(self.map)
                    if self.map.battle.attacker_won:
                        town = self.map.GetTownAt(self.map.battle.heroA.x, self.map.battle.heroA.y)
                        if town:
                            self.map.players[self.map.battle.heroA.player_idx].TakeTown(town)
                    del self.map.battle
                    self.map.battle = None
                    # TODO: find a better way to insert a "frame" with the adventure map after a battle is over
                    if self.actions_log.callback:
                        self.actions_log.callback(True)
        else:
            action.player_idx = self.map.curr_player_idx if not self.map.hero_leveling_up else self.map.hero_leveling_up.player_idx
            action.is_accepted = self.AcceptAction(action)
            if action.is_accepted:
                action.is_valid = action.ApplyAction(self)
                # not accepted actions should not count, otherwise we might end up in an invalid state, e.g.:
                #       * hero leveling up, and trying to end turn for the player without completing the skill choice
                #       * hero leveling up for the other player (not current player), and counting invalid actions towards the current player instead!
                #       * trying to force an end turn while there is a battle ongoing (when playable battles without autocombat will be supported)
                self.actions_this_turn += 1
        
        self.actions_log.LogAction(action)
        
        if self.check_same_action_in_succession:
            # for debgging built-in AI, remove before training
            if self.prev_action_str == jsonpickle.encode(action):
                #self.reload_curr_day = True
                raise RuntimeError(f'Duplicate action detected :  {self.prev_action_str}')
            self.prev_action_str = jsonpickle.encode(action)

        # TODO: revisit this hack to separate auto-combat and adventure-map actions
        if self.IsBattleOngoing() and self.only_autocombat:
            self.map.battle.AutoCombat(self.actions_log)

            # TODO: revisit this the level-up implementation
            level_up = self.map.battle.ApplyResult(self.map)
            if self.map.hero_leveling_up:
                last_action = self.actions_log.actions[-1]
                last_action.dbg_info = f'{"attacker" if self.map.battle.attacker_won else "defender"} won, hero of P{1+self.map.hero_leveling_up.player_idx} waiting levelup'
            if self.map.battle.attacker_won:
                # town = self.map.GetTownAt(self.map.battle.heroA.x, self.map.battle.heroA.y)
                town = self.map.GetTownAt(self.map.battle.heroA.x, self.map.battle.heroA.y) if not self.map.battle.armyD.town else self.map.battle.armyD.town
                if town:
                    self.map.players[self.map.battle.heroA.player_idx].TakeTown(town)
            del self.map.battle
            self.map.battle = None
            # TODO: find a better way to insert a "frame" with the adventure map after a battle is over
            if self.actions_log.callback:
                self.actions_log.callback(True)
        
        if self.map.hero_leveling_up and self.autoskill_existing[self.map.hero_leveling_up.player_idx]:
            # this automatically makes the skill choice, when configured
            from HOMM.HOMMActions import ActionSkillChoice
            while self.map.hero_leveling_up:
                self.DoAction(ActionSkillChoice(0))

        if action.type == 'end turn':
            self.actions_this_turn = 0
        elif self.actions_this_turn >= self.max_actions_turn and not self.map.hero_leveling_up:
            # TODO: force end turn?
            # ok = self.DoAction(HOMMAction.END_TURN)
            ok = self.DoAction(HOMMAction.NewEndTurn())
            assert ok
        
        self.CheckVictory()

        # for debgging built-in AI, remove before training
        if self.reload_prev_day:
            assert(self.prev_day_state)
            self.LoadState(self.prev_day_state)
            self.reload_prev_day = False
            return False
        elif self.reload_curr_day:
            assert(self.curr_day_state)
            self.LoadState(self.curr_day_state)
            self.reload_curr_day = False
            return False

        # is this extra protection of action type needed?
        if not self.auto_playing_builtin_ai and action.type in ['end turn', 'skill choice']:
            self.ContinueAuto()

        return action.is_valid


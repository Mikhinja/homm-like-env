from HOMM.Battle import Battle
import HOMM.HOMMAPI
from HOMM.HOMMData.HOMMHeroData import HeroSkills
from HOMM.HOMMData.HOMMMapData import MapObjTypeById, TileTypesByName
import HOMM.HOMMEnv
from HOMM.HOMMUnitTypes import UnitUtils
from HOMM.Hero import Hero
from HOMM.Town import TownBase

class ActionMoveHero(HOMM.HOMMAPI.HOMMAction):
    def __init__(self, hero_idx:int, dest:tuple[int,int]) -> None:
        super().__init__('move hero')
        self.hero_idx = hero_idx
        self.dest = dest
        self.end_pos:tuple[int,int]=None
        self.start_pos:tuple[int,int]=None

    def ApplyAction(self, env:HOMM.HOMMEnv.HOMMSimpleEnv) -> bool:
        super().ApplyAction(env)
        assert env and env.map
        assert env.map.curr_player_idx == self.player_idx
        assert not (env.map.battle or env.map.hero_leveling_up) # is this still needed?
        player = env.map.players[self.player_idx]
        if len(player.heroes) > self.hero_idx:
            hero:Hero = player.heroes[self.hero_idx]
            self.start_pos = self.end_pos = (hero.x, hero.y)
            self.result_what = f'{hero.name} at {self.start_pos} to {self.dest}' # TODO: revisit this
            if env.map.IsInBounds(*self.dest) and self.start_pos != self.dest and hero.curr_movement > 0:
                path = env.map.FindPathTo(hero, *self.dest)
                if path:
                    if any([pos for pos in path[:-1] if not env.map.CanStepOn(hero, *pos)]):
                        print('break')
                    env.map.tiles[0, hero.x,hero.y] = TileTypesByName['free']
                    # env.map.Clear_Cached_gScores(hero=hero) # need to clear cache since the hero will move
                    env.map.Clear_Cached_gScores() # need to clear all the cache since the hero will move

                    town:TownBase = env.map.GetTownAt(*path[-1])
                    for pos in path:
                        # TODO: performance imprvement: get the distances with the path function, so we don't compute them again
                        dist = env.map.Adj_Dist(hero.x, hero.y, *pos)
                        if dist > hero.curr_movement:
                            hero.curr_movement = 0 # should recheck this
                            break

                        hero.curr_movement -= dist

                        if env.map.CanStepOn(hero, *pos):
                            hero.x, hero.y = pos
                            player.ScoutCircle(pos, hero.GetScoutingRadius())
                            if town and pos == self.dest:
                                self.result = f'{town.faction} '
                                self.result += 'taken' if player.TakeTown(town) else 'visited'
                                hero.Visit(town)
                                self.result_where = str(pos)
                        else:
                            assert pos == self.dest, f'pathing error, tile was {env.map.tiles[0,pos[0],pos[1]]}'
                            self.result_where = str(pos)
                            if town:
                                if town.player_idx != player.idx:
                                    town_owner = env.map.players[town.player_idx]
                                    heroDef:Hero = next((h for h in town_owner.heroes if (h.x, h.y) == pos), None)
                                    if heroDef:
                                        armyDef = heroDef.army
                                        if town.army and any(town.army):
                                            heroDef.army.Combine(town.army)
                                        env.map.battle = Battle(hero, armyDef, layout='normal', rng=env.rs)
                                        self.result = f'battle {town.faction}, {heroDef.name}'
                                    else:
                                        if town.army and any(town.army):
                                            env.map.battle = Battle(hero, town.army, layout='normal', rng=env.rs)
                                            self.result = f'battle {town.faction}'
                                        else:
                                            player.TakeTown(town)
                                            self.result = f'{town.faction} taken'
                                else:
                                    hero.Visit(town)
                                    self.result = f'{town.faction} visited'
                            elif env.map.tiles[0, pos[0],pos[1]] == TileTypesByName['resource']:
                                # give the resource to player
                                self.result = f'take resource {MapObjTypeById[env.map.resources[pos].res_type]}'
                                hero.ReceiveResources(env.map.TakeResource(*pos))
                            elif env.map.tiles[0, pos[0],pos[1]] == TileTypesByName['hero or army']:
                                # TODO: replace this with HOMMMAP method to get hero at
                                heroDef = next((h for h in env.map.heroes if (h.x, h.y) == pos), None)
                                if (not heroDef) or heroDef.player_idx != hero.player_idx:
                                    self.result = 'battle '
                                    if heroDef:
                                        armyDef = heroDef.army
                                        self.result += heroDef.name
                                    else:
                                        armyDef = next(a for a in env.map.neutral_armies if (a.x, a.y) == pos)
                                        self.result += f'neutral {armyDef.stacks[0].GetUnitName()}'
                                    
                                    # TODO: implement creature banks (layout 'ambush')
                                    env.map.battle = Battle(hero, armyDef, layout='normal', rng=env.rs)
                            else:
                                # TODO implement artifacts
                                pass

                    self.end_pos = (hero.x, hero.y)
                    self.result_what += f' end {self.end_pos}'
                    env.map.tiles[0, hero.x,hero.y] = TileTypesByName['hero or army']
                    return True
        else:
            self.result_what = f'{self.hero_idx} to {self.dest}'
        return False

class ActionBuild(HOMM.HOMMAPI.HOMMAction):
    def __init__(self, town_idx:int, building_name:str) -> None:
        super().__init__('build')
        self.town_idx = town_idx
        self.building_name = building_name

    def ApplyAction(self, env:HOMM.HOMMEnv.HOMMSimpleEnv) -> bool:
        super().ApplyAction(env)
        player = env.map.players[env.map.curr_player_idx]
        town = player.towns[self.town_idx] if len(player.towns) > self.town_idx else None
        if town:
            self.result_what = self.building_name
            if town.Build(self.building_name):
                self.result = 'built'
                self.result_where = str((town.x, town.y))
                return True
        return False

class ActionRecruitArmy(HOMM.HOMMAPI.HOMMAction):
    def __init__(self, town_idx:int, unit_type:int, amount:int) -> None:
        super().__init__('recruit army')
        self.town_idx = town_idx
        self.stack_idx = unit_type
        self.amount = amount

    def ApplyAction(self, env:HOMM.HOMMEnv.HOMMSimpleEnv) -> bool:
        super().ApplyAction(env)
        player = env.map.players[env.map.curr_player_idx]
        town:TownBase = player.towns[self.town_idx] if len(player.towns) > self.town_idx else None
        self.result_what = ''
        if town:
            if self.stack_idx >= 0:
                # should this be recruit by unit type instead?
                if self.__recruit_at_idx__(town, self.stack_idx, self.amount) > 0:
                    return True
            else:
                recruited = [self.__recruit_at_idx__(town, idx, self.amount) for idx in range(6, -1, -1)]
                if any(recruited):
                    return True
        return False
    def __recruit_at_idx__(self, town:TownBase, idx:int, amount:int) -> int:
        unit_type = town.GetUnitTypeOfLevel(idx+1)
        stack = next((stack for stack in town.army if stack.unit_type==unit_type), None) if town.army else None
        prev_count = stack.num if stack else 0
        if town.RecruitByLevel(amount=amount, unit_lvl=idx+1):
            stack = next(stack for stack in town.army if stack.unit_type==unit_type)
            self.result_what += f'{stack.num - prev_count} {UnitUtils.GetUnitName(stack.unit_type)} '
            self.result = 'recruited'
            self.result_where = f'{town.faction} at ({town.x:>2}, {town.y:>2})'
            return stack.num - prev_count

class ActionTransferArmy(HOMM.HOMMAPI.HOMMAction):
    def __init__(self, stack_idx:int, amount:int, src_town_idx:int=-1, src_hero_idx:int=-1, dest_town_idx:int=-1, dest_hero_idx:int=-1) -> None:
        super().__init__('transfer army')
        self.stack_idx = stack_idx
        self.amount = amount
        self.src_town_idx = src_town_idx
        self.src_hero_idx = src_hero_idx
        self.dest_town_idx = dest_town_idx
        self.dest_hero_idx = dest_hero_idx

    def ApplyAction(self, env:HOMM.HOMMEnv.HOMMSimpleEnv) -> bool:
        super().ApplyAction(env)
        assert self.src_town_idx>=0 or self.src_hero_idx>=0
        assert self.dest_town_idx>=0 or self.dest_hero_idx>=0
        # cannot transfer army from one town directly to another town
        if not (self.src_town_idx>=0 and self.dest_town_idx>=0):
            player = env.map.players[env.map.curr_player_idx]
            if self.src_town_idx >= 0:
                src_town:TownBase = player.towns[self.src_town_idx] if len(player.towns) > self.src_town_idx else None
                if src_town and src_town.army and sum(stack.num for stack in src_town.army) > 1:
                    self.result_where = f'from {src_town.faction} at {(src_town.x, src_town.y)}'
                    if self.dest_hero_idx >= 0:
                        dest_hero = player.heroes[self.dest_hero_idx] if len(player.heroes) > self.dest_hero_idx else None
                        if dest_hero:
                            if (dest_hero.x, dest_hero.y) == (src_town.x, src_town.y):
                                if self.stack_idx < 0: # hack to take all
                                    self.result_what = 'entire army'
                                    if dest_hero.army.Combine(src_town.army):
                                        self.result = f'transferred to {dest_hero.name}'
                                        return True
                                elif src_town.army and len(src_town.army.stacks) > self.stack_idx:
                                    self.result_what = f'{self.amount} of {src_town.army.stacks[self.stack_idx].num} {UnitUtils.GetUnitName(src_town.army.stacks[self.stack_idx].unit_type)}'
                                    if dest_hero.army.TakeOne(src_town.army, self.stack_idx, self.amount):
                                        self.result = f'transferred to {dest_hero.name}'
                                        return True
                    elif self.dest_town_idx >= 0:
                        self.result = 'transfer army directly between towns not allowed'
                        pass # transfer army directly between towns not supported!
            elif self.src_hero_idx >= 0:
                src_hero = player.heroes[self.src_hero_idx] if len(player.heroes) > self.src_hero_idx else None
                if src_hero and sum(stack.num for stack in src_hero.army) > 1:
                    self.result_where = f'from {src_hero.name} at {(src_hero.x, src_hero.y)}'
                    if self.dest_hero_idx >= 0:
                        dest_hero = player.heroes[self.dest_hero_idx] if len(player.heroes) > self.dest_hero_idx else None
                        if dest_hero:
                            if env.map.__are_neighbors__(src_hero.x, src_hero.y, dest_hero.x, dest_hero.y):
                                if self.stack_idx < 0: # hack to take all
                                    self.result_what = 'entire army'
                                    if dest_hero.army.Combine(src_hero.army):
                                        self.result = f'transferred to {dest_hero.name}'
                                        # cannot leave hero with no army
                                        # TODO: revisit this, make it more robust
                                        return src_hero.army.TakeOne(dest_hero.army, 0, 1)
                                elif len(src_hero.army.stacks) > self.stack_idx:
                                    unit_type = src_hero.army.stacks[self.stack_idx].unit_type
                                    self.result_what = f'{self.amount} of {src_hero.army.stacks[self.stack_idx].num} {UnitUtils.GetUnitName(unit_type)}'
                                    if dest_hero.army.TakeOne(src_hero.army, self.stack_idx, self.amount):
                                        if not any([stack for stack in src_hero.army.stacks if stack.num > 0]):
                                            dest_idx = next(idx for idx, stack in enumerate(dest_hero.army.stacks) if stack.unit_type == unit_type)
                                            src_hero.army.TakeOne(dest_hero, dest_idx, 1)
                                        self.result = f'transferred to {dest_hero.name}'
                                        return True
                    elif self.dest_town_idx >= 0:
                        dest_town:TownBase = player.towns[self.dest_town_idx] if len(player.towns) > self.dest_town_idx else None
                        if dest_town:
                            if (src_hero.x, src_hero.y) == (dest_town.x, dest_town.y):
                                if not dest_town.army:
                                    dest_town.army = HOMM.HOMMAPI.HOMMArmy(stacks=[])
                                if self.stack_idx < 0: # hack to take all
                                    self.result_what = 'entire army'
                                    if dest_town.army.Combine(src_hero.army):
                                        self.result = f'transferred to {dest_town.faction}'
                                        # cannot leave hero with no army
                                        # TODO: revisit this, make it more robust
                                        return src_hero.army.TakeOne(dest_town.army, 0, 1)
                                elif len(src_hero.army.stacks) > self.stack_idx:
                                    self.result_what = f'{self.amount} of {src_hero.army.stacks[self.stack_idx].num} {UnitUtils.GetUnitName(src_hero.army.stacks[self.stack_idx].unit_type)}'
                                    if dest_town.army.TakeOne(src_hero.army, self.stack_idx, self.amount):
                                        if not any([stack for stack in src_hero.army.stacks if stack.num > 0]):
                                            dest_idx = next(idx for idx, stack in enumerate(src_hero.army.stacks) if stack.unit_type == unit_type)
                                            src_hero.army.TakeOne(dest_town, dest_idx, 1)
                                        self.result = f'transferred to {dest_town.faction}'
                                        return True
        return False

class ActionRecruitHero(HOMM.HOMMAPI.HOMMAction):
    def __init__(self, town_idx:int) -> None:
        super().__init__('recruit hero')
        self.town_idx = town_idx
        # TODO: implement hero choices when recruiting

    def ApplyAction(self, env:HOMM.HOMMEnv.HOMMSimpleEnv) -> bool:
        super().ApplyAction(env)
        player = env.map.players[env.map.curr_player_idx]
        town:TownBase = player.towns[self.town_idx] if len(player.towns) > self.town_idx else None
        # recruited = next(hero for hero in self.map.heroes if hero.player_idx == -1)
        # TODO: implement this with a saved state somehow
        recruited:Hero = env.rs.choice([hero for hero in env.map.heroes if hero.player_idx == -1])
        if town and recruited:
            if player.PayCost([2500] + [0]*6):
                if env.map.GiveHeroTo(recruited, player, (town.x, town.y)):
                    recruited.ResetStartingArmy(give_starting_army=player.heroes_recruited_this_week < 2)
                    player.heroes_recruited_this_week += 1
                    self.result_what = f'{recruited.name}'
                    self.result = 'recruited'
                    self.result_where = f'from {town.faction} at {(recruited.x, recruited.y)}'
                    return True
        return False

class ActionSkillChoice(HOMM.HOMMAPI.HOMMAction):
    def __init__(self, option:int) -> None:
        super().__init__('skill choice')
        self.choice = option

    def ApplyAction(self, env:HOMM.HOMMEnv.HOMMSimpleEnv) -> bool:
        super().ApplyAction(env)
        if env.map.hero_leveling_up:
            self.player_idx = env.map.hero_leveling_up.player_idx # should this be done here?
            option1, option2 = env.map.hero_leveling_up.GetSkillChoices()
            if self.choice not in (option1, option2) and self.choice in [0,1]:
                self.choice = (option1, option2)[self.choice]
            if self.choice in (option1, option2):
                hero = env.map.hero_leveling_up
                if hero.SkillLevelUp(self.choice):
                    self.result_what = f'{HeroSkills[self.choice][0]}'
                    self.result = f'level {hero.GetSkillLevel(self.choice)}'
                    return True
        return False

class ActionChangeSelection(HOMM.HOMMAPI.HOMMAction):
    def __init__(self, sel_hero_idx:int=None, sel_town_idx:int=None) -> None:
        super().__init__(action_type='select')
        assert sel_hero_idx is None or sel_town_idx is None
        assert (sel_hero_idx is not None and sel_hero_idx >= 0) or (sel_town_idx is not None and sel_town_idx >= 0)
        self.sel_hero_idx = sel_hero_idx
        self.sel_town_idx = sel_town_idx

    def ApplyAction(self, env:HOMM.HOMMEnv.HOMMSimpleEnv) -> bool:
        player = env.map.players[env.map.curr_player_idx]
        if self.sel_hero_idx is not None:
            if len(player.heroes) > self.sel_hero_idx:
                player.sel_hero_idx = self.sel_hero_idx+1
                self.result = f'Selected hero {self.sel_hero_idx}'
                self.result_what = player.heroes[self.sel_hero_idx].name
                return True
        else:
            if len(player.heroes) > self.sel_town_idx:
                player.sel_town_idx = self.sel_town_idx+1
                self.result = f'Selected town {self.sel_town_idx}'
                self.result_what = player.towns[self.sel_town_idx].faction
                return True
        return False

class ActionEndTurn(HOMM.HOMMAPI.HOMMAction):
    def __init__(self) -> None:
        super().__init__('end turn')
    def ApplyAction(self, env:HOMM.HOMMEnv.HOMMSimpleEnv) -> bool:
        super().ApplyAction(env)
        if not env.ended:
            day_over = env.map.EndTurn()
            if day_over:
                self.result = 'day over'
                env.DayOver()
            return True
        return False
    @staticmethod
    def NewEndTurn() -> HOMM.HOMMAPI.HOMMAction:
        a = ActionEndTurn()
        a.is_forced = True
        return a

# this is needed to be able to apply an end turn action from anywhere
HOMM.HOMMAPI.HOMMAction.NewEndTurn = ActionEndTurn.NewEndTurn

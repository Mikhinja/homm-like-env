
import math
from turtle import Vec2D
from HOMM.HOMMAPI import HOMMAI, HOMMAction, HOMMArmy, HOMMHero, HOMMPlayer
from HOMM.HOMMActions import ActionEndTurn, ActionMoveHero, ActionRecruitArmy, ActionRecruitHero, ActionSkillChoice, ActionTransferArmy
from HOMM.HOMMData.HOMMTownData import TownTypes
from HOMM.HOMMEnv import HOMMSimpleEnv
from HOMM.HOMMUnitTypes import UnitUtils
from HOMM.Hero import Hero
from HOMM.Town import TownBase


# TODO: replace these with some lightweight geometry library
def normalize_vec2d(vec:tuple[float,float]) -> Vec2D:
    length = math.sqrt(vec[0]**2 + vec[1]**2)
    return Vec2D(vec[0]/length, vec[1]/length)

class DummyAI(HOMMAI):
    def __init__(self, env:HOMMSimpleEnv, player:HOMMPlayer) -> None:
        super().__init__(env, player)
        self.env = env
        self.player = player
        self.player.ai = self # is this ok?
    def GetNextAction(self) -> HOMMAction:
         return ActionEndTurn()

class ProceduralAI(HOMMAI):
    # difficulties and persionalities inspired by description here https://heroes.thelazy.net/index.php/Difficulty_level
    PERSONALITIES = ['explorer', 'builder', 'warrior']
    DIFFICULTIES = ['easy', 'normal', 'hard']
    def __init__(self, env:HOMMSimpleEnv, player:HOMMPlayer, personality:str='explorer', difficulty:str='easy') -> None:
        super().__init__(env, player)
        assert(personality in ProceduralAI.PERSONALITIES)
        assert(difficulty in ProceduralAI.DIFFICULTIES)
        self.personality = personality
        self.difficulty = difficulty
        self.last_day_built = -1 # for easy and normal difficulties
        self.env = env
        self.player = player
        self.player.ai = self # is this ok?

        self.max_heroes = 2 # easy
        self.army_str_ratio = 1.5
        if self.difficulty == 'normal':
            self.max_heroes = 3
            self.army_str_ratio = 1.2
        elif self.difficulty == 'hard':
            self.max_heroes = 4
            self.army_str_ratio = 1.0
    
    @staticmethod
    def EstimateArmyStrength(army:HOMMArmy) -> int:
        ret = army.GetAIVal()
        if army.hero:
            ret *= math.sqrt((1 + army.hero.attack * 0.05) * (1 + army.hero.defense * 0.05))
        return int(ret)

    def GetNextAction(self) -> HOMMAction:
        # TODO: implement personalities
        # TODO: implement town building
        act_level_up = self.LevelUpHero()
        if act_level_up:
            act_level_up.is_from_proceduralAI=True
            return act_level_up
        
        act_buy_army = self.BuyArmy()
        if act_buy_army:
            act_buy_army.is_from_proceduralAI=True
            return act_buy_army
        
        act_buy_hero = self.BuyHero()
        if act_buy_hero:
            act_buy_hero.is_from_proceduralAI=True
            return act_buy_hero
        
        if len(self.player.towns) == 0:
            # preioritize capturing at least 1 town
            act_take_town = self.SeekTown()
            if act_take_town:
                act_take_town.is_from_proceduralAI=True
                return act_take_town
        
        act_take_army = self.HeroTakeArmy()
        if act_take_army:
            act_take_army.is_from_proceduralAI=True
            return act_take_army

        act_avoid = self.AvoidHeroBattle()
        if act_avoid:
            act_avoid.is_from_proceduralAI=True
            return act_avoid
        
        act_pickup, dist = self.SeekResource()
        if act_pickup:
            act_pickup.is_from_proceduralAI=True
            return act_pickup
        
        act_take_town = self.SeekTown()
        if act_take_town:
            act_take_town.is_from_proceduralAI=True
            return act_take_town
        
        act_battle_hero = self.SeekHeroBattle()
        if act_battle_hero:
            act_battle_hero.is_from_proceduralAI=True
            return act_battle_hero
        
        act_battle_neutral, dist = self.SeekNeutralBattle()
        if act_battle_neutral:
            act_battle_neutral.is_from_proceduralAI=True
            return act_battle_neutral
        
        act_scout_about = self.ScoutAbout()
        if act_scout_about:
            act_scout_about.is_from_proceduralAI=True
            return act_scout_about
        
        act_end_turn = ActionEndTurn()
        act_end_turn.is_from_proceduralAI=True
        return act_end_turn
    
    def SeekResource(self) -> tuple[HOMMAction, int]:
        if len(self.env.map.resources) > 0 and len(self.player.heroes) > 0:
            all_possibilities = [(idx, pos, self.env.map.FindPathTo(hero, *pos))
                for idx, hero in enumerate(self.player.heroes) if hero.curr_movement > 0
                for pos in self.env.map.resources if self.player.CanSee(*pos)]
            all_possibilities = [p for p in all_possibilities if p[2]]
            if all_possibilities:
                # not ideal because it is not actually movement cost, but "Mahnattan-ish" distance (number of adjacent steps)
                all_possibilities.sort(key=lambda x: len(x[2])) # lambda h, p, d: d
                hero_idx, pos, dist = all_possibilities[0]
                # dist is currently not used, but it could be used to prioritize actions based on proximity
                return ActionMoveHero(hero_idx=hero_idx, dest=pos), dist
        return None, 0
    
    def BuyHero(self) -> HOMMAction:
        if self.player.resources[0] > 2500 and (len(self.player.heroes) < self.max_heroes
                and len(self.player.heroes) < self.env.map.MAX_PLAYER_HEROES):
            town = next((town for town in self.player.towns if not any(
                hero for hero in self.player.heroes if hero.x == town.x and hero.y == town.y)), None)
            if town:
                return ActionRecruitHero(self.player.towns.index(town))
        return None
    
    def BuyArmy(self) -> HOMMAction:
        if len(self.player.towns) > 0 and self.player.resources[0] > 500:
            for idx, town in enumerate(self.player.towns):
                ttown:TownBase = town
                stack_idx, num = next(((idx, num) for idx, num in enumerate(ttown.creature_bank) if num > 0), (None, None))
                if stack_idx and num:
                    # TODO: implement proper unit upgrades
                    # lvl, num = x
                    # unit_id = next(unit_id for unit_id in TownTypes[ttown.faction]['Units'] if UnitUtils.GetUnitLevel(unit_id)==lvl)
                    # return ActionRecruitArmy(town_idx=idx, unit_type=unit_id, amount=num)
                    return ActionRecruitArmy(town_idx=idx, unit_type=stack_idx, amount=num)
        return None
    
    def SeekHeroBattle(self) -> HOMMAction:
        if len(self.player.heroes) > 0:
            other_players = [other_player for other_player in self.env.map.players if other_player != self.player]
            all_enemy_heroes = [target_hero for other_player in other_players for target_hero in other_player.heroes]
            all_viable_pairs = [(my_hero_idx, target_hero, self.env.map.FindPathTo(my_hero, target_hero.x, target_hero.y))
                for target_hero in all_enemy_heroes if self.player.CanSee(target_hero.x, target_hero.y)
                for my_hero_idx, my_hero in enumerate(self.player.heroes) if my_hero.curr_movement > 0
                if self.EstimateArmyStrength(my_hero.army) * self.army_str_ratio > self.EstimateArmyStrength(target_hero.army)
            ]
            all_viable_pairs = [p for p in all_viable_pairs if p[2]]
            if all_viable_pairs:
                all_viable_pairs.sort(key=lambda x: len(x[2]))
                hero_idx, target, dist = all_viable_pairs[0]
                return ActionMoveHero(hero_idx=hero_idx, dest=(target.x, target.y))

        return None
    
    def SeekNeutralBattle(self) -> tuple[HOMMAction, int]:
        if len(self.player.heroes) > 0:
            all_targets = [(idx, (narmy.x, narmy.y), self.env.map.FindPathTo(hero, narmy.x, narmy.y))
                for idx, hero in enumerate(self.player.heroes) if hero.curr_movement > 0
                for narmy in self.env.map.neutral_armies if self.player.CanSee(narmy.x, narmy.y)
                    and self.EstimateArmyStrength(hero.army) * self.army_str_ratio > self.EstimateArmyStrength(narmy)]
            all_targets = [t for t in all_targets if t[2]] # strip the unreachable
            if all_targets:
                all_targets.sort(key=lambda x: len(x[2]))
                hero_idx, pos, dist = all_targets[0]
                return ActionMoveHero(hero_idx=hero_idx, dest=pos), dist
        return None, 0
    
    def SeekTown(self) -> HOMMAction:
        # if len(self.player.heroes) > 0:
        if any(hero for hero in self.player.heroes if hero.curr_movement > 0) > 0:
            target_towns = [town for town in self.env.map.towns
                if town.player_idx != self.player.idx and self.player.CanSee(town.x, town.y)]
            if target_towns:
                target_towns = [(town, sorted([(my_hero_idx, self.env.map.FindPathTo(my_hero, town.x, town.y))
                        for my_hero_idx, my_hero in enumerate(self.player.heroes) if my_hero.curr_movement > 0],
                        key=lambda x: len(x[1]) if x[1] else math.inf)
                    ) for town in target_towns]
                target_towns = [tt for tt in target_towns if tt[1][0][1]]
                if target_towns:
                    target_town, hero_list = min(target_towns, key=lambda x: len(x[1][0][1]))
                    return ActionMoveHero(hero_list[0][0], (target_town.x, target_town.y))

        return None
    
    def AvoidHeroBattle(self) -> HOMMAction:
        if len(self.player.heroes) > 0:
            steps = int(max(Hero.BASE_MOVEMENT.values()) / 100)
            other_players = [other_player for other_player in self.env.map.players if other_player != self.player]
            all_enemy_heroes = [target_hero for other_player in other_players for target_hero in other_player.heroes]
            # tuples with own hero in peril and a list of perils (enemy heroes) for each of them
            all_perils = [(my_hero_idx, [(target_hero, self.env.map.FindPathTo(my_hero, target_hero.x, target_hero.y)) for target_hero in all_enemy_heroes
                    if self.player.CanSee(target_hero.x, target_hero.y)
                    and self.EstimateArmyStrength(my_hero.army) * self.army_str_ratio < self.EstimateArmyStrength(target_hero.army)
                ]) for my_hero_idx, my_hero in enumerate(self.player.heroes) if my_hero.curr_movement > 0
            ]
            # keep as perils only enemy heroes that can reach us in 1 turn (estimate)
            all_perils = [(p[0], [pp[0] for pp in p[1] if pp[1] and steps-1 > len(pp[1])]) for p in all_perils]
            # keep only own heroes that are threatened by at least one
            all_perils = [(my_hero_idx, perils) for my_hero_idx, perils in all_perils if len(perils) > 0]
            while len(all_perils) > 0:
                my_hero_idx, perils = all_perils.pop()
                my_hero = self.player.heroes[my_hero_idx]
                perils = [(peril, len(self.env.map.FindPathTo(my_hero, peril.x, peril.y))) for peril in perils]

                sum_of_distances = sum(d for p, d in perils)
                max_of_distances = 1 + max(d for p, d in perils)
                # the perils are weighted according to their proximity
                vecs = [Vec2D(  (p.x - my_hero.x) * ((max_of_distances - d) / sum_of_distances),
                                (p.y - my_hero.y) * ((max_of_distances - d) / sum_of_distances))
                    for p, d in perils]
                flee_x = sum(vec[0] for vec in vecs) / len(vecs)
                flee_y = sum(vec[1] for vec in vecs) / len(vecs)
                if not (flee_x or flee_y):
                    # left or right? up or down? can't decide!
                    continue
                flee_dir = normalize_vec2d(Vec2D(-flee_x, -flee_y)) # run the other way
                assert(flee_dir[0] != 0 or flee_dir[1] != 0)
                flee_x, flee_y = flee_dir
                flee_x = max(0, min(self.env.map.size[0]-1, my_hero.x + int(flee_dir[0] * steps)))
                flee_y = max(0, min(self.env.map.size[1]-1, my_hero.y + int(flee_dir[1] * steps)))
                if (my_hero.x, my_hero.y) != (flee_x, flee_y) and (self.env.map.CanStepOn(my_hero, flee_x, flee_y)
                        and not self.env.map.__are_neighbors__(my_hero.x, my_hero.y, flee_x, flee_y)):
                    path = self.env.map.FindPathTo(my_hero, flee_x, flee_y, ignore_visibility=True)
                    if path:
                        for pos in path[::-1]:
                            if self.player.CanSee(*pos):
                                # TODO: check if we should remember past actions to avoid looping the same attempted "flee"
                                return ActionMoveHero(my_hero_idx, pos)
        
        return None
    
    def ScoutAbout(self):
        if len(self.player.heroes) > 0:
            my_hero_idx = next((idx for idx, hero in enumerate(self.player.heroes) if hero.curr_movement > 0), None)
            if my_hero_idx is not None:
                my_hero:HOMMHero = self.player.heroes[my_hero_idx]
                scout_border = []
                for x in range(self.env.map.size[0]):
                    for y in range(self.env.map.size[1]):
                        if self.player.visibility[x,y] and self.env.map.CanStepOn(my_hero, x, y):
                            neighbors = [(x+dx, y+dy) for dy in [-1,0,1] for dx in [-1,0,1] if (dx!=0 or dy!=0)]
                            for nx,ny in neighbors:
                                if self.env.map.IsInBounds(nx, ny) and not self.player.visibility[nx,ny]:
                                    scout_border.append((x, y))
                                    break
                if scout_border:
                    idx = self.env.rs.randint(0, len(scout_border))
                    while scout_border and not self.env.map.FindPathTo(my_hero, *scout_border[idx]):
                        del scout_border[idx]
                        if scout_border:
                            idx = self.env.rs.randint(0, len(scout_border))
                    if scout_border:
                        return ActionMoveHero(my_hero_idx, dest=scout_border[idx])
        return None
    
    def HeroTakeArmy(self):
        if len(self.player.heroes) > 0 and len(self.player.towns) > 0:
            towns = [(idx, t) for idx,t in enumerate(self.player.towns) if t.army and any([s for s in t.army.stacks if s.num > 0])]
            if towns:
                towns_pos = [(t.x, t.y) for _,t in towns]
                my_hero_idx = next((idx for idx, hero in enumerate(self.player.heroes) if (hero.x, hero.y) in towns_pos), None)
                if my_hero_idx is None:
                    my_hero_idx = next((idx for idx, hero in enumerate(self.player.heroes) if hero.curr_movement > 0), None)
                    if my_hero_idx is not None and self.env.map.FindPathTo(self.player.heroes[my_hero_idx], *towns_pos[0]):
                        return ActionMoveHero(my_hero_idx, towns_pos[0])
                else:
                    my_hero:HOMMHero = self.player.heroes[my_hero_idx]
                    town_idx, ttown = next(((idx,t) for (idx,t) in towns if t.x==my_hero.x and t.y==my_hero.y))
                    stack_idx = next((idx for idx,stack in enumerate(ttown.army.stacks) if stack and stack.num>0))
                    return ActionTransferArmy(stack_idx=stack_idx, amount=1000, src_town_idx=town_idx, dest_hero_idx=my_hero_idx)
        return None
    
    def LevelUpHero(self):
        if self.env.map.hero_leveling_up:
            option1, option2 = self.env.map.hero_leveling_up.GetSkillChoices()
            return ActionSkillChoice(option1)
        return None

class PartialDummmyAI(ProceduralAI):
    def __init__(self, env: HOMMSimpleEnv, player: HOMMPlayer, dummy_after_day:int=3) -> None:
        super().__init__(env, player, personality='explorer', difficulty='easy')
        self.dummy_after_day = dummy_after_day
    def GetNextAction(self) -> HOMMAction:
        if self.env.map.day < self.dummy_after_day:
            return super().GetNextAction()
        return ActionEndTurn()

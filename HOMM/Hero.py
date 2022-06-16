#from Army import Army, ArmyInCombat
from shutil import which
from numpy.random import RandomState
from HOMM.HOMMData.HOMMHeroData import HeroSpells, HeroClasses, HeroDefinitions, HeroLevelExperience, HeroSkills
from HOMM.HOMMData.HOMMMapData import TileTypesByName
from HOMM.HOMMHeroes import HeroSkillUtils, HeroSpellUtils, HeroUtils
from HOMM.HOMMAPI import HOMMHero, HOMMArmy, HOMMArmyStack, HOMMMap, HOMMPlayer, HOMMTown

class Hero(HOMMHero):
    BASE_MOVEMENT = {
         3:	1500,
         4:	1560,
         5:	1630,
         6:	1700,
         7:	1760,
         8:	1830,
         9:	1900,
        10:	1960,
        11: 2000, # for speed 11 or more
    }
    def __init__(self, x:int, y:int, player_idx:int, rng:RandomState, hero_def_name:str='Might Archery Offense') -> None:
        super().__init__(x, y, player_idx, rng)
        self.name = hero_def_name
        hero_def = HeroDefinitions[self.name]
        self.hero_class = HeroClasses[hero_def[0]]
        start_stats = self.hero_class['primary stats']['initial']
        self.attack = start_stats[0]
        self.defense = start_stats[1]
        self.power = start_stats[2]
        self.knowledge = start_stats[3]
        self.skills = [0] * len(HeroSkills)
        self.skills[hero_def[1]] += 1
        self.skills[hero_def[2]] += 1
        self.rng = rng
        self.ResetStartingArmy()
        self.skill_option_1:int = None
        self.skill_option_2:int = None
        # this is for convenience, see ReceiveResources
        self.owner:HOMMPlayer = None
        self.map:HOMMMap = None
        self.stables_visited = False

    def DayOver(self, newDayNum:int):
        if newDayNum % 7 == 0:
            self.stables_visited = False
        min_army_speed = min(11, min(stack.GetUnitSpeed() for stack in self.army if stack))
        self.curr_movement = Hero.BASE_MOVEMENT[min_army_speed]
        if self.stables_visited:
            self.curr_movement += 400
        self.curr_mana += 1 if self.curr_mana < self.GetMaxMana() else 0

    def ReceiveResources(self, res:list):
        if len(res) == 8:
            self.GainXP(res[7])
        self.owner.ReceiveResources(res[:7])
    def Visit(self, town:HOMMTown):
        assert(town)
        for spell_id in town.spells:
            self.LearnSpell(spell_id)
        # TODO: implement other buildings with visits, such as permanent stats bonuses and stables for weekly movement bonus
    def ResetStartingArmy(self, give_starting_army:bool=True):
        if self.army:
            del self.army
        if give_starting_army:
            self.army:HOMMArmy = HOMMArmy([HOMMArmyStack(unit_id=si[0], num=self.rng.randint(si[1], si[2])) for si in HeroDefinitions[self.name][3]])
        else:
            self.army:HOMMArmy = HOMMArmy(stacks=[HOMMArmyStack(unit_id=HeroDefinitions[self.name][3][0][0], num=1)])
        self.army.hero = self
    
    def GainXP(self, xp: int):
        lvl_before = self.GetLevel()
        self.xp += xp
        lvl_after = self.GetLevel()
        self.waiting_skill_choice = lvl_after - lvl_before
        if self.waiting_skill_choice > 0:
            self.map.hero_leveling_up = self
            for lvl in range(lvl_before + 1, lvl_after + 1):
                self.StatsLevelUp(lvl)

    def GetSkillLevel(self, skill_id:int) -> int:
        lvl = self.skills[skill_id]
        assert(lvl >= 0 and lvl <= 3)
        return lvl
    def GetSkillValue(self, skill_id:int):
        return HeroSkillUtils.GetSkillValue(skill_id, self.GetSkillLevel(skill_id))
    def GetSpellLevel(self, spell_id:int) -> int:
        if spell_id in self.spells:
            magic_school_id = HeroSpells[spell_id][5]
            # 3..6 are the school of magic skills
            if magic_school_id >=3 and magic_school_id <= 6:
                return self.GetSkillLevel(magic_school_id)
            else:
                if magic_school_id != -1:
                    raise RuntimeError(f'Hero Spell [{HeroSpells[spell_id][0]}] magic school id is invalid: {magic_school_id}!')
                return max(self.GetSkillLevel(3), self.GetSkillLevel(4), self.GetSkillLevel(5), self.GetSkillLevel(6))
        return -1
    def GetSpellCost(self, spell_id:int) -> int:
        if spell_id in self.spells:
            if self.GetSpellLevel(spell_id) > 0:
                return HeroSpells[spell_id][9]
            else:
                return HeroSpells[spell_id][10]
        return 9999 # hack to mark not usable spell
    def GetSpellValue(self, spell_id:int) -> int:
        assert(spell_id in self.spells)
        spell_lvl = self.GetSpellLevel(spell_id)
        if spell_lvl >= 0:
            if spell_lvl == 0:
                spell_lvl = 1 # workaround, since the difference between none and basic is just the spell points cost
            # base + spell power * modifier
            return HeroSpells[spell_id][spell_lvl] + (self.power * HeroSpells[spell_id][4])
        return 0 # TODO: check if this is ok
    def Defeated(self):
        assert(self.map.hero_leveling_up != self)
        self.map.tiles[0, self.x, self.y] = TileTypesByName['free']
        self.x = self.y = -1
        player_prev = self.map.players[self.player_idx]
        player_prev.heroes.remove(self)
        player_prev.sel_hero_idx = 1 if player_prev.heroes else 0
        self.player_idx = -1
        self.owner = None
    def GetSkillChoices(self) -> tuple[int,int]:
        assert(self.waiting_skill_choice > 0)
        # TODO: implement proper skill choices, according to hero class specifications: https://heroes.thelazy.net/index.php/Secondary_skill
        if self.skill_option_1 is None:
            available = [i for i,x in enumerate(self.skills) if x>0 and x<3]
            not_learnt = [i for i,x in enumerate(self.skills) if x==0]
            #self.skill_option_1 = self.skill_option_2 = None
            if available:
                self.skill_option_1 = available[self.rng.randint(0, len(available))]
                self.skill_option_2 = not_learnt[self.rng.randint(0, len(not_learnt))]
            else:
                curr_skill_count = sum(1 for x in self.skills if x>0)
                if curr_skill_count < self.MAX_SKILLS:
                    self.skill_option_1 = not_learnt[self.rng.randint(0, len(not_learnt))]
                    if curr_skill_count < self.MAX_SKILLS - 1:
                        self.skill_option_2 = not_learnt[self.rng.randint(0, len(not_learnt))]
                    else:
                        self.skill_option_2 = None
        return self.skill_option_1, self.skill_option_2
    
    def StatsLevelUp(self, lvl:int):
        if lvl < 10:
            which_prob = 'prob 2-9'
        else:
            which_prob = 'prob 10+'
        what = self.rng.choice(['attack', 'defense', 'power', 'knowledge'], 1, p=self.hero_class['primary stats'][which_prob])
        setattr(self, what[0], 1 + getattr(self, what[0]))

    def SkillLevelUp(self, skill_id:int) -> bool:
        assert(self.map.hero_leveling_up == self and skill_id in (self.skill_option_1, self.skill_option_2))
        curr_skill_count = sum(1 for x in self.skills if x>0)
        assert(self.skills[skill_id] > 0 or curr_skill_count < self.MAX_SKILLS)
        if self.skills[skill_id] < 3:
            self.skills[skill_id] += 1
            self.waiting_skill_choice -= 1
            if self.waiting_skill_choice == 0:
                self.map.hero_leveling_up = None
            self.skill_option_1 = self.skill_option_2 = None
            return True
        return False
    def LearnSpell(self, spell_id:int) -> bool:
        if not spell_id in self.spells:
            self.spells.append(spell_id)

    def IsOnMap(self) -> bool:
        return self.x>=0 and self.y>=0 and self.x<self.map.size[0] and self.y<self.map.size[1]
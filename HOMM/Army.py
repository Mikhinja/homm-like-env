from HOMM.HOMMData.HOMMHeroData import HeroSpells
from HOMM.HOMMHeroes import HeroUtils
from HOMM.HOMMUnitTypes import UnitUtils
from HOMM.HOMMAPI import HOMMArmyStack, HOMMArmyStackInCombat, HOMMHero

# is this one actually needed?
class ArmyStack(HOMMArmyStack):
    def __init__(self, num: int, unit_id: int = None, unit_name: str = None, hero:HOMMHero=None):
        super().__init__(num, unit_id, unit_name)
        self.hero = hero

    def GetUnitSpeed(self):
        bonus = self.hero.GetBonus('speed') if self.hero else 0
        return bonus + super().GetUnitSpeed()

# is this one actually needed?
class ArmyStackInCombat(HOMMArmyStackInCombat):
    def __init__(self, stack: HOMMArmyStack, orig_idx: int, x: int, y: int, hero: HOMMHero = None):
        super().__init__(stack, orig_idx, x, y, hero)

    def GetUnitSpeed(self):
        bonus = self.hero.GetBonus('speed') if self.hero else 0
        return bonus + self.stack.GetUnitSpeed()

# is this one actually needed?
class ArmyIter(object):
    def __init__(self, army):
        self.parent = army
        self.idx = 0
    def __next__(self) -> ArmyStack:
        curr_idx = self.idx
        self.idx += 1
        if curr_idx < 7:
            return self.parent.GetStackAt(curr_idx)
        else:
            self.idx = 0
            raise StopIteration

# is this one actually needed?
class Army(object):
    def __init__(self, arr_vals_army_stacks:list, arr_vals_hero:list=None):
        pass

    def GetStackAt(self, idx:int) -> ArmyStack:
        pass
    def GetAIVal(self) -> int:
        return sum(self.GetStackAt(idx).GetAIVal() for idx in range(7))
    def __iter__(self) -> ArmyIter:
        return ArmyIter(self)

# is this one actually needed?
class ArmyInCombat(object):
    def __init__(self, army:Army):
        self.army:Army = army
        self.combat_data = [[idx, stack.GetAIVal(), -1] for idx, stack in enumerate(self.army)]


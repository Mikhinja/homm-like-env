from numpy.random import RandomState
from HOMM.HOMMAPI import HOMMArmy, HOMMArmyStack, HOMMPlayer, HOMMTown
from HOMM.HOMMData.HOMMTownData import TownTypes
from HOMM.HOMMData.HOMMUnitData import UnitTypes
from HOMM.HOMMHeroes import HeroSpellUtils
from HOMM.HOMMUnitTypes import UnitUtils


class TownBase(HOMMTown):
    def __init__(self, x:int, y:int, rng:RandomState, faction:str='Castle', has_fort:bool=True) -> None:
        super().__init__(x, y, rng)
        self.faction = faction
        self.owner:HOMMPlayer = None
        self.built_today = False
        self.Build('Village Hall') # all towns have Village Hall
        if has_fort:
            self.built_today = False
            self.Build('Fort')
        self.built_today = False
        
    def DayOver(self, newDayNum: int):
        if self.owner:
            # generate income
            self.owner.ReceiveResources(self.income)

            if any(b for b in self.buildings if 'Mage Guild' in b):
                # refill mana
                # TODO: revisit this implementation when teams will be implemented, visiting heroes could be from an allied player
                for h in [h for h in self.owner.heroes if (h.x, h.y) == (self.x, self.y)]:
                    if h.curr_mana < h.GetMaxMana():
                        h.curr_mana = h.GetMaxMana()
        if newDayNum % 7 == 0:
            self.creature_bank = [self.creature_bank[i] + self.creature_growth[i] for i in range(7)]
        self.built_today = False
        
    def GetCostOfBuilding(self, building_name:str) -> list[int]:
        return TownTypes[self.faction]['Buildings'][building_name]['cost']
    def Build(self, building_name:str) -> bool:
        assert(building_name and building_name in TownTypes[self.faction]['Buildings'])
        if not self.built_today and building_name not in self.buildings:
            building_def = TownTypes[self.faction]['Buildings'][building_name]
            assert(building_def)
            # if there is no player just build it, it's fine, just build it
            can_afford = self.owner.PayCost(building_def['cost']) if self.owner else True
            if can_afford:
                self.buildings.append(building_name)
                if 'income' in building_def:
                    new_income = building_def['income']
                    assert(len(self.income) == 7 and len(new_income) == 7)
                    if sum(new_income) > 0:
                        self.income = [self.income[i] + new_income[i] for i in range(7)]
                if self.owner: # game engine can build how many buildings it wants
                    self.built_today = True

                # mage guilds give spells to visiting heroes
                # TODO: implement spell book - some heroes must buy spell book to learn spells, other heroes start with a spell book
                if 'Mage Guild' in building_name:
                    lvl = int(building_name[-1])
                    possible_spells = HeroSpellUtils.GetSpellsOfLevel(lvl)
                    self.spells += list(self.rng.choice(possible_spells, 6 - lvl))
                return True
        return False
    @DeprecationWarning
    def GetBuildingDef(self, building_idx:int):
        b_key = next(b_key for b_key in TownTypes[self.faction]['Buildings'] if TownTypes[self.faction]['Buildings'][b_key]['id'] == building_idx)
        return TownTypes[self.faction]['Buildings'][b_key]
    
    def GetUnitTypeOfLevel(self, unit_lvl:int) -> int:
        building = next((bn for bn in self.buildings
                if 'prod' in TownTypes[self.faction]['Buildings'][bn]
                and UnitUtils.GetUnitLevel(UnitUtils.GetUnitTypeByName(
                    TownTypes[self.faction]['Buildings'][bn]['prod'])) == unit_lvl
            ), None)
        if building:
            return UnitUtils.GetUnitTypeByName(TownTypes[self.faction]['Buildings'][building]['prod'])
        return 0 # is this ok?

    def __recruit__(self, amount:int, idx:int, unit_type:int) -> bool:
        if self.owner:
            available_amount = min(amount, self.creature_bank[idx])
            existing = next((stack for stack in self.army if stack.unit_type == unit_type), None) if self.army else None
            has_room = True if existing else (not self.army or len(self.army.stacks) < 7)
            if has_room:
                # TODO: improve this implementation
                actual_amount = min(available_amount, int(self.owner.resources[0] / UnitUtils.GetUnitCost(unit_type)))
                cost = [actual_amount * UnitUtils.GetUnitCost(unit_type)] + [0] * 6
                if self.owner.PayCost(cost):
                    if existing:
                        existing.num += available_amount
                    else:
                        new_stack = HOMMArmyStack(available_amount, unit_id=unit_type)
                        if self.army:
                            self.army.stacks.append(new_stack)
                        else:
                            self.army = HOMMArmy([new_stack], self.x, self.y)
                            self.army.town = self
                    self.creature_bank[idx] -= available_amount
                    return True
        return False

    def RecruitByLevel(self, amount: int, unit_lvl: int) -> bool:
        idx = unit_lvl-1
        if amount > 0 and self.creature_bank[idx] > 0 and self.owner:
            building = next((bn for bn in self.buildings
                if 'prod' in TownTypes[self.faction]['Buildings'][bn]
                and UnitUtils.GetUnitLevel(UnitUtils.GetUnitTypeByName(
                    TownTypes[self.faction]['Buildings'][bn]['prod'])) == unit_lvl
            ), None)
            if building:
                unit_type = UnitUtils.GetUnitTypeByName(TownTypes[self.faction]['Buildings'][building]['prod'])
                return self.__recruit__(amount, idx, unit_type)
        return False
    
    def Recruit(self, amount:int, unit_type:int) -> bool:
        idx = UnitUtils.GetUnitLevel(unit_type)-1
        building = next((bn for bn in self.buildings
            if 'prod' in TownTypes[self.faction]['Buildings'][bn] and TownTypes[self.faction]['Buildings'][bn]['prod'] == UnitUtils.GetUnitName(unit_type)
        ), None)
        if amount > 0 and self.creature_bank[idx] > 0 and self.owner and building:
            return self.__recruit__(amount, idx, unit_type)
        return False
    

class CastleTown(TownBase):
    def __init__(self, x: int, y: int, rng:RandomState, has_fort: bool = True) -> None:
        super().__init__(x, y, rng, faction='Castle', has_fort=has_fort)
        
    # TODO: move this to base!
    def Build(self, building_name:str) -> bool:
        built = super().Build(building_name)
        if built:
            building_def = TownTypes[self.faction]['Buildings'][building_name]
            assert(building_def)
            if 'prod' in building_def:
                unit_id = UnitUtils.GetUnitTypeByName(building_def['prod'])
                unit_bank_idx = UnitUtils.GetUnitLevel(unit_id) -1
                self.creature_growth[unit_bank_idx] = UnitUtils.GetUnitTypeGrowth(unit_id)
                self.creature_bank[unit_bank_idx] += self.creature_growth[unit_bank_idx]

        return built
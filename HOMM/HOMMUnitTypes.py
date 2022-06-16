from HOMM.HOMMData.HOMMUnitData import UnitTypes

class UnitUtils:
    @staticmethod
    def GetUnitName(unit_type_id:int) -> str:
        return UnitTypes[unit_type_id][1]
    
    @staticmethod
    def GetUnitTypeByName(unit_type_name:str=None) -> int:
        if unit_type_name:
            return next(i for i in UnitTypes if UnitTypes[i][1].casefold() == unit_type_name.casefold())
        return 0
    @staticmethod
    def GetUnitTypeGrowth(unit_type_id:int) -> int:
        return UnitTypes[unit_type_id][12]
    
    @staticmethod
    def GetUnitLevel(unit_type_id:int) -> int:
        return UnitTypes[unit_type_id][11]
    
    @staticmethod
    def GetUnitCost(unit_type_id:int) -> int:
        return UnitTypes[unit_type_id][13]

    @staticmethod
    def GetDamage(unit_type_id:int):
        return UnitTypes[unit_type_id][4], UnitTypes[unit_type_id][5]
    
    @staticmethod
    def GetAttack(unit_type_id:int) -> int:
        return UnitTypes[unit_type_id][2]

    @staticmethod
    def GetDefense(unit_type_id:int) -> int:
        return UnitTypes[unit_type_id][3]
    
    @staticmethod
    def IsRanged(unit_type_id:int) -> bool:
        return UnitTypes[unit_type_id][10] > 0
    @staticmethod
    def IsFlying(unit_type_id:int) -> bool:
        return UnitTypes[unit_type_id][8] == 'Flying'
    
    @staticmethod
    def IsUnitUpgraded(unit_type_id:int) -> bool:
        return UnitTypes[unit_type_id][0] != unit_type_id
    
    @staticmethod
    def GetSpeed(unit_type_id:int) -> int:
        return UnitTypes[unit_type_id][7]
    
    @staticmethod
    def GetHealth(unit_type_id:int) -> int:
        return UnitTypes[unit_type_id][6]
    
    @staticmethod
    def GetMaxShots(unit_type_id:int) -> int:
        return UnitTypes[unit_type_id][10]

    @staticmethod
    def GetAIValue(unit_type_id:int) -> int:
        return UnitTypes[unit_type_id][-1]
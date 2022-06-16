from HOMM.HOMMData.HOMMHeroData import HeroLevelExperience, HeroSkills, HeroClasses, HeroSpells
from HOMM.HOMMUnitTypes import UnitUtils
import sys


class HeroSkillUtils:
    @staticmethod
    def GetSkillId(skill_name:str) -> int:
        return next(key for key in HeroSkills if HeroSkills[key][0].casefold() == skill_name.casefold())
    @staticmethod
    @DeprecationWarning
    def GetSkillLevel(hero_skills:list, skill_id:int) -> int:
        lvl = 0
        if hero_skills:
            lvl = hero_skills[1].count(skill_id)
        if lvl > 3:
            lvl = 3
            print(None, sys.stderr, 'Hero Skill [' + HeroSkills[skill_id][0] + '] Level Greater than 3!')
        return lvl
    @staticmethod
    def GetSkillValue(skill_id:int, skill_level:int):
        if skill_level > 0:
            return HeroSkills[skill_id][skill_level]
        else:
            return 0
    @staticmethod
    def GetArcheryLevel(hero_skills:list) -> int:
        return HeroSkillUtils.GetSkillLevel(hero_skills, 0)
    @staticmethod
    def GetArcheryValue(hero_skills:list):
        return HeroSkillUtils.GetSkillValue(hero_skills, 0)
    @staticmethod
    def GetOffenseLevel(hero_skills:list) -> int:
        return HeroSkillUtils.GetSkillLevel(hero_skills, 1)
    @staticmethod
    def GetOffenseValue(hero_skills:list):
        return HeroSkillUtils.GetSkillValue(hero_skills, 1)
    @staticmethod
    def GetArmorerLevel(hero_skills:list) -> int:
        return HeroSkillUtils.GetSkillLevel(hero_skills, 2)
    @staticmethod
    def GetArmorerValue(hero_skills:list):
        return HeroSkillUtils.GetSkillValue(hero_skills, 2)
    @staticmethod
    def GetAirMagicLevel(hero_skills:list) -> int:
        return HeroSkillUtils.GetSkillLevel(hero_skills, 3)
    @staticmethod
    def GetAirMagicValue(hero_skills:list):
        return HeroSkillUtils.GetSkillValue(hero_skills, 3)
    @staticmethod
    def GetEarchMagicLevel(hero_skills:list) -> int:
        return HeroSkillUtils.GetSkillLevel(hero_skills, 4)
    @staticmethod
    def GetEarthMagicValue(hero_skills:list):
        return HeroSkillUtils.GetSkillValue(hero_skills, 4)
    @staticmethod
    def GetFireMagicLevel(hero_skills:list) -> int:
        return HeroSkillUtils.GetSkillLevel(hero_skills, 5)
    @staticmethod
    def GetFireMagicValue(hero_skills:list):
        return HeroSkillUtils.GetSkillValue(hero_skills, 5)
    @staticmethod
    def GetWaterMagicLevel(hero_skills:list) -> int:
        return HeroSkillUtils.GetSkillLevel(hero_skills, 6)
    @staticmethod
    def GetWaterMagicValue(hero_skills:list):
        return HeroSkillUtils.GetSkillValue(hero_skills, 6)

class HeroSpellUtils:
    @staticmethod
    def GetSpellName(spell_id:int) -> str:
        return HeroSpells[spell_id][0]
    @staticmethod
    def GetSpellId(spell_name:str) -> int:
        return next(key for key in HeroSpells if HeroSpells[key][0].casefold() == spell_name.casefold())
    
    @staticmethod
    def GetSpellsOfLevel(level:int):
        return [spell_id for spell_id in HeroSpells if HeroSpells[spell_id][6] == level]
    
    @staticmethod
    @DeprecationWarning
    def GetSpellLevel(hero_skills:list, spell_id:int) -> int:
        magic_school_id = HeroSpells[spell_id][5]
        if magic_school_id >=3 and magic_school_id <= 6:
            return HeroSkillUtils.GetSkillLevel(hero_skills, magic_school_id)
        else:
            if magic_school_id != -1:
                print(None, sys.stderr, 'Hero Spell [' + HeroSpells[spell_id][0] + '] magic school id is invalid: ' + magic_school_id + '!')
            return max(HeroSkillUtils.GetSkillLevel(hero_skills, 3),
                HeroSkillUtils.GetSkillLevel(hero_skills, 4),
                HeroSkillUtils.GetSkillLevel(hero_skills, 5),
                HeroSkillUtils.GetSkillLevel(hero_skills, 6))
    @staticmethod
    def GetSpellCost(hero_skills:list, spell_id:int) -> int:
        spell_lvl = HeroSpellUtils.GetSpellLevel(hero_skills, spell_id)
        if spell_lvl > 0:
            return HeroSpells[spell_id][9]
        else:
            return HeroSpells[spell_id][10]
    @staticmethod
    @DeprecationWarning
    def GetSpellValue(hero_attr:list, hero_skills:list, spell_id:int):
        spell_lvl = HeroSpellUtils.GetSpellLevel(hero_skills, spell_id)
        if spell_lvl == 0:
            spell_lvl = 1 # workaround, since the difference between none and basic is just the spell points cost
        # base + spell power * modifier
        value = HeroSpells[spell_id][spell_lvl]
        if hero_attr:
            value += hero_attr[2] * HeroSpells[spell_id][4]
        return value

    @staticmethod
    def GetShieldLevel(hero_skills:list) -> int:
        return HeroSpellUtils.GetSpellLevel(hero_skills, 0)
    @staticmethod
    def GetAirShieldLevel(hero_skills:list) -> int:
        return HeroSpellUtils.GetSpellLevel(hero_skills, 1)
    
    @staticmethod
    @DeprecationWarning
    def GetSpellDuration(army_stack:list, spell_id:int):
        if army_stack:
            return army_stack[4][spell_id]
        return 0
    
    @staticmethod
    def IsSpellBuff(spell_id:int) -> bool:
        # TODO: make a better implementation, more generic than this
        return spell_id in [0, 1, 4, 5, 8, 10, 11, 12, 14, 15, 20]
    @staticmethod
    def IsSpellCurse(spell_id:int) -> bool:
        # TODO: make a better implementation, more generic than this
        return spell_id in [10, 16, 17, 18]
    @staticmethod
    def IsSpellDamage(spell_id:int) -> bool:
        # TODO: make a better implementation, more generic than this
        return spell_id in [2, 3, 6, 7, 9, 13, 19]
    @staticmethod
    def IsSpellFrenezy(spell_id:int) -> bool:
        # TODO: make a better implementation, more generic than this
        return spell_id == 10
    
class HeroUtils:
    @staticmethod
    @DeprecationWarning
    def GetArmyStackSpellEffect(army_stack:list, hero_attr:list, hero_skills:list, spell_id:int):
        duration = HeroSpellUtils.GetSpellDuration(army_stack, spell_id)
        if duration > 0:
            return HeroSpellUtils.GetSpellValue(hero_attr, hero_skills, spell_id)
        else:
            return 0
    
    @staticmethod
    @DeprecationWarning
    def XPtoLevel(xp:int) -> int:
        i, xp_next_level = next([(i, x) for i, x in enumerate(HeroLevelExperience) if x > xp])
        return i, xp_next_level
    @staticmethod
    @DeprecationWarning
    def GetHeroLevel(hero_attr:list) -> int:
        return HeroUtils.XPtoLevel(hero_attr[4])
    @staticmethod
    def GetHeroSpellPower(hero_attr:list) -> int:
        return hero_attr[2]

    @staticmethod
    def GetArmyStackShieldEffect(army_stack:list, hero_attr:list, hero_skills:list):
        return HeroUtils.GetArmyStackSpellEffect(army_stack, hero_attr, hero_skills, 0)
    
    @staticmethod
    def GetArmyStackAirShieldEffect(army_stack:list, hero_attr:list, hero_skills:list):
        return HeroUtils.GetArmyStackSpellEffect(army_stack, hero_attr, hero_skills, 1)
    
    @staticmethod
    @DeprecationWarning
    def GetArmyStackDamage(army_stack:list, hero_attr:list, hero_skills:list):
        dmg_min, dmg_max = UnitUtils.GetDamage(army_stack[0])
        duration_bless = HeroSpellUtils.GetSpellDuration(army_stack, 11) # 11 is bless
        duration_curse = HeroSpellUtils.GetSpellDuration(army_stack, 16) # 16 is bless
        
        if duration_bless > 0:
            dmg_min = dmg_max = dmg_max + HeroUtils.GetArmyStackSpellEffect(army_stack, hero_attr, hero_skills, 11)
        elif duration_curse > 0:
            dmg_min = dmg_max = dmg_min + HeroUtils.GetArmyStackSpellEffect(army_stack, hero_attr, hero_skills, 16)
        return dmg_min, dmg_max
    
    @staticmethod
    @DeprecationWarning
    def GetArmyStackAttackDefense(army_stack:list, hero_attr:list, hero_skills:list):
        atk_bonus = hero_attr[0]
        def_bonus = hero_attr[1]

        atk_unit = UnitUtils.GetAttack(army_stack[0])
        def_unit = UnitUtils.GetDefense(army_stack[0])

        # spells: 5=Stoke Skin, 8=Bloodlust, 10=Frenzy, 14=Prayer, 15=Precision, 17=Weakness
        
        atk_bonus += HeroUtils.GetArmyStackSpellEffect(army_stack, hero_attr, hero_skills, 17) # weakness
        def_bonus += HeroUtils.GetArmyStackSpellEffect(army_stack, hero_attr, hero_skills, 5) # stone skin
        
        if not UnitUtils.IsRanged(army_stack[0]):
            atk_bonus += HeroUtils.GetArmyStackSpellEffect(army_stack, hero_attr, hero_skills, 8) # bloodlust
        else:
            atk_bonus += HeroUtils.GetArmyStackSpellEffect(army_stack, hero_attr, hero_skills, 14) # precision
        
        prayer_bonus = HeroUtils.GetArmyStackSpellEffect(army_stack, hero_attr, hero_skills, 13) # prayer
        atk_bonus += prayer_bonus
        def_bonus += prayer_bonus
        
        if HeroSpellUtils.GetSpellDuration(army_stack, 10) > 0: 
            # frenzy - this needs to be last, and under if
            atk_bonus += (def_unit + def_bonus) * HeroUtils.GetArmyStackSpellEffect(army_stack, hero_attr, hero_skills, 10)
            def_bonus = def_unit = 0

        return atk_unit + atk_bonus, def_unit + def_bonus
    
    @staticmethod
    @DeprecationWarning
    def GetArmyStackSpeed(army_stack:list, hero_artif:list, hero_skills:list):
        if army_stack:
            # TODO: support for artifacts
            speed = UnitUtils.GetSpeed(army_stack[0])
            speed += HeroUtils.GetArmyStackSpellEffect(army_stack, [], hero_skills, 4) # 4 is haste
            speed *= (1 - HeroUtils.GetArmyStackSpellEffect(army_stack, [], hero_skills, 18))
            return speed
        return 0
    
    @staticmethod
    @DeprecationWarning
    def GetArmyStackProtectionForSpellType(army_stack:list, hero_skills:list, spell_id:int):
        # currently there is only one protection spell: protection from air id=20
        protection = 0
        if HeroSpells[spell_id][5] == 3 or HeroSpells[spell_id] == -1: # Air
            # 20 is protection from air
            protection = HeroUtils.GetArmyStackSpellEffect(army_stack, [], hero_skills, 20)
        return protection
    
    @staticmethod
    @DeprecationWarning
    def GetArmyStackHealth(army_stack:list, hero_artif:list) -> int:
        # TODO: support for artifacts
        return army_stack[1] * UnitUtils.GetHealth(army_stack[0])


from email.policy import default
from inspect import stack
import math
from turtle import Vec2D
from HOMM.HOMMData.HOMMTownData import TownTypes
from HOMM.HOMMHeroes import HeroSkillUtils, HeroSpellUtils, HeroUtils
from HOMM.HOMMUnitTypes import UnitUtils
from HOMM.Battlefield import Battlefield
from HOMM.HOMMAPI import HOMMAI, HOMMAction, HOMMArmy, HOMMArmyInCombat, HOMMArmyStackInCombat, HOMMAutoCombatAI, HOMMBattlefield, HOMMHero, HOMMPlayer
from HOMM.Town import TownBase

CAST_SPELL_ARMY_RATIO_THRESHOLD = 0.9

# from first to last, not a complete list of all supported spells, just a reduced list for AI
# the built-in auto-combat AI only "knows" to use these spells
SPELL_PRIORITY = [
    14, # prayer            - water
    0,  # shield            - earth
    1,  # air shield        - air
    6,  # meteor shower     - earth
    7,  # implosion         - earth
    19, # inferno           - fire
    9,  # fireball          - fire
    18, # slow              - earth
    4,  # haste             - air
    11, # bless             - water
    5,  # stone skin        - earth
    3,  # lightning bolt    - air
    2,  # magic arrow       - all
]

class BattleAction(HOMMAction):
    BATTLE_ACTION_TYPES = ['spell', 'shoot', 'move', 'move attack']
    def __init__(self, battle_action_type: str) -> None:
        assert(battle_action_type in BattleAction.BATTLE_ACTION_TYPES)
        super().__init__('battle action')
        self.battle_action_type = battle_action_type
        self.target_pos:tuple[int,int]=None
        self.spell_id:int=-1
        self.dest:tuple[int,int]=None
        self.end_pos:tuple[int,int]=None
        self.start_pos:tuple[int,int]=None
    
    @staticmethod
    def Move(dest_x:int, dest_y:int):
        action = BattleAction('move')
        action.dest = (dest_x, dest_y)
        return action
    @staticmethod
    def MoveAttack(dest_x:int, dest_y:int, target_x:int, target_y:int):
        action = BattleAction('move attack')
        action.dest = (dest_x, dest_y)
        # hack to specify the stack to be attacked
        action.target_pos = (target_x, target_y)
        return action
    @staticmethod
    def Shoot(target_x:int, target_y:int):
        action = BattleAction('shoot')
        # hack to specify the stack to be attacked
        action.target_pos = (target_x, target_y)
        return action
    @staticmethod
    def Spell(spell_idx:int, target_x:int, target_y:int):
        action = BattleAction('spell')
        action.spell_id = spell_idx
        action.result_what = spell_idx # TODO: revisit this hacky way of marking the spell id
        action.target_pos = (target_x, target_y)
        return action

class AutoCombatAI(HOMMAutoCombatAI):
    def __init__(self) -> None:
        super().__init__()
    def GetNextBattleAction(self, currArmy: HOMMArmyInCombat, currStack: HOMMArmyStackInCombat, otherArmy: HOMMArmyInCombat,
            battlefield:HOMMBattlefield, spellAllowed: bool = False) -> HOMMAction:
        # TODO: when implementing summon spells update the restriction for max stack idx
        assert(currArmy and otherArmy and battlefield and currStack)
        if spellAllowed and currArmy.GetAIVal() < CAST_SPELL_ARMY_RATIO_THRESHOLD * otherArmy.GetAIVal():
            spell_cast = self.PickBestSpell(currArmy, otherArmy)
            if spell_cast:
                spell_id, target_stack = spell_cast
                return BattleAction.Spell(spell_id, target_stack.x, target_stack.y)
        
        # TODO: implement rules for retreat and surrender here

        assert(currStack.curr_num > 0)
        
        target_stack:HOMMArmyStackInCombat = max(otherArmy, key=lambda stack:stack.GetAIVal())
        if target_stack.curr_num <= 0:
            raise RuntimeError('No target or already dead!')
        
        # TODO: revisit this when implementing forgetfullness spell
        if UnitUtils.IsRanged(currStack.stack.unit_type) and currStack.shots > 0:
            return BattleAction.Shoot(target_stack.x, target_stack.y)
        else:
            # TODO: implement pathing for flying movement!
            next_pos = battlefield.GetClosestToTarget(currStack, target_stack, otherHero=otherArmy.hero)
            if next_pos:
                if battlefield.AreNeighbors(next_pos, (target_stack.x, target_stack.y)):
                    return BattleAction.MoveAttack(*next_pos, target_stack.x, target_stack.y)
                else:
                    return BattleAction.Move(*next_pos)
            else:
                # TODO: implement a better way to skip a move that doesn't have a path
                return BattleAction.Move(currStack.x, currStack.y)

    def PickBestSpell(self, currArmy: HOMMArmyInCombat, otherArmy: HOMMArmyInCombat):
        if currArmy.hero:
            spells = [spell_id for spell_id in SPELL_PRIORITY
                    if currArmy.hero.GetSpellLevel(spell_id)>=0 and
                        currArmy.curr_mana >= currArmy.hero.GetSpellCost(spell_id)]
            for spell in spells:
                target = self.PickBestStackForSpell(currArmy, otherArmy, spell)
                if HeroSpellUtils.IsSpellBuff(spell) or HeroSpellUtils.IsSpellCurse(spell):
                    if target.active_spells[spell] == 0:
                        return spell, target
        return None
    def PickBestStackForSpell(self, currArmy: HOMMArmyInCombat, otherArmy: HOMMArmyInCombat, spell_id:int) -> HOMMArmyStackInCombat:
        candidate = None
        
        if HeroSpellUtils.IsSpellBuff(spell_id):
            # TODO: implement spells that can be cast on dead stacks, such as resurrection, this needs to be changed
            candidate_stacks = sorted([stack for stack in currArmy if stack.curr_num>0], reverse=True, key=lambda s:s.GetAIVal())
            if HeroSpellUtils.GetSpellId('Precision') == spell_id:
                candidate = next(x for x in candidate_stacks if UnitUtils.IsRanged(x[2]))
            elif HeroSpellUtils.GetSpellId('Bloodlust') == spell_id:
                candidate = next(x for x in candidate_stacks if not UnitUtils.IsRanged(x[2]))
            else:
                candidate = next(x for x in candidate_stacks)
        else:
            candidate_stacks = sorted([stack for stack in otherArmy if stack.curr_num>0], reverse=True, key=lambda s:s.GetAIVal())
            candidate = next((x for x in candidate_stacks), None)
        
        return candidate



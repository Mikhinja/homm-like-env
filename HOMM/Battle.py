from numpy.random import RandomState, Generator, MT19937
from HOMM.Army import Army, ArmyInCombat
from HOMM.Battlefield import Battlefield
from HOMM.HOMMAPI import HOMMActionLogger, HOMMArmy, HOMMArmyInCombat, HOMMArmyStackInCombat, HOMMAutoCombatAI, HOMMBattle, HOMMBattleFactory, HOMMHero, HOMMMap
from HOMM.HOMMBuiltInAI_Battle import AutoCombatAI, BattleAction
from HOMM.HOMMHeroes import HeroSkillUtils, HeroUtils, HeroSpellUtils
from HOMM.HOMMUnitTypes import UnitUtils
from HOMM.Hero import Hero

class Battle(HOMMBattle):
    MAX_ROUNDS = 100
    def __init__(self, heroA: Hero, armyD: HOMMArmy, layout:str, rng:RandomState, ai:HOMMAutoCombatAI=AutoCombatAI(), max_rounds:int=MAX_ROUNDS) -> None:
        super().__init__(heroA=heroA, armyD=armyD, layout=layout, rng=rng)
        self.max_rounds = max_rounds
        self.curr_round = -1 # not started
        self.layout = layout
        self.ai = ai
        self.results_applied = False
        self.battlefield = None
        self.rng = rng
        self.Reset()

    def AutoCombat(self, action_log:HOMMActionLogger=None):
        assert(self.ai)
        while not self.IsBattleOver():
            self.NewRound()
            while self.curr_stack and not self.IsBattleOver():
                if self.attacker_action:
                    action = self.ai.GetNextBattleAction(self.armyA, self.curr_stack, self.armyD, self.battlefield, not self.atk_round_spell)
                    action.player_idx = self.armyA.hero.player_idx if self.armyA.hero else -1
                else:
                    action = self.ai.GetNextBattleAction(self.armyD, self.curr_stack, self.armyA, self.battlefield, not self.def_round_spell)
                    action.player_idx = self.armyD.hero.player_idx if self.armyD.hero else self.armyD.town.player_idx if self.armyD.town else -1
                action.is_valid = self.DoAction(action)
                if action_log:
                    action_log.LogAction(action)
        # nothing to do here, the results can be taken anytime later, see GetResult

    def GetResult(self) -> tuple:
        assert(self.IsBattleOver())
        if not self.results_computed:
            self.armyA.army.sort(key=lambda stack: stack.orig_idx)
            self.armyD.army.sort(key=lambda stack: stack.orig_idx)
            self.xp_reward = 0
            if self.armyD.IsDefeated():
                self.attacker_won = True
                health_initially = sum(stack.num * UnitUtils.GetHealth(stack.unit_type) for stack in self.armyD.orig_army)
                health_now = sum(stack.curr_num * UnitUtils.GetHealth(stack.stack.unit_type) for stack in self.armyD)
                if self.armyD.orig_army.hero:
                    self.xp_reward += 500
            else:
                self.attacker_won = False
                health_initially = sum(stack.num * UnitUtils.GetHealth(stack.unit_type) for stack in self.armyA.orig_army)
                health_now = sum(stack.curr_num * UnitUtils.GetHealth(stack.stack.unit_type) for stack in self.armyA)
                if self.armyA.orig_army.hero:
                    self.xp_reward += 500
            
            self.xp_reward += health_initially - health_now
        
        # TODO: return losses on both sides, useful for replaying a battle
        return self.attacker_won, self.xp_reward
    
    def Reset(self):
        # TODO: save-restore rng state for repeatability on reset
        assert(not self.results_applied)
        if self.battlefield:
            del self.armyA
            del self.armyD
            del self.battlefield
            self.armyA = None
            self.armyD = None
            self.battlefield = None
        layoutA = 'left'
        layoutD = 'right'
        if self.layout == 'ambush':
            layoutA = 'center'
            layoutD = 'surround'
        self.armyA = HOMMArmyInCombat(self.heroA.army, layoutA)
        self.armyD = HOMMArmyInCombat(self.orig_armyD, layoutD)

        # TODO: implement obstacles
        self.battlefield = Battlefield(self.armyA, self.armyD)
        self.results_computed = False

    def ApplyResult(self, the_map:HOMMMap) -> bool:
        assert((not self.results_applied) and self.armyA.hero)
        # ensure we have up to date values
        self.GetResult()

        # this should never be reset, applying results of a battle should NOT be repeatable
        self.results_applied = True

        # update both armies
        for idx in range(len(self.armyA.army)):
            self.armyA.orig_army.stacks[idx].num = self.armyA.army[idx].curr_num
        for idx in range(len(self.armyD.army)):
            self.armyD.orig_army.stacks[idx].num = self.armyD.army[idx].curr_num
        
        # update heroes' mana
        if self.armyA.hero:
            self.armyA.hero.curr_mana = self.armyA.curr_mana
        if self.armyD.hero:
            self.armyD.hero.curr_mana = self.armyD.curr_mana

        if self.attacker_won:
            if self.armyD.hero:
                if self.armyD.IsDefeated():
                    self.armyD.hero.Defeated()
            elif not self.armyD.town:
                if self.armyD.IsDefeated():
                    the_map.RemoveNeutralArmy(self.armyD.orig_army)
            
            self.armyA.hero.GainXP(self.xp_reward)

            return self.armyA.hero.waiting_skill_choice > 0
        else:
            if self.armyA.IsDefeated():
                self.armyA.hero.Defeated()
            
            if self.armyD.hero:
                self.armyD.hero.GainXP(self.xp_reward)

                return self.armyD.hero.waiting_skill_choice > 0
        return False

    def RefreshStackOrder(self):
        self.armyA.army.sort(key=lambda stack: stack.GetUnitSpeed(self.armyD.hero), reverse=True)
        self.armyD.army.sort(key=lambda stack: stack.GetUnitSpeed(self.armyA.hero), reverse=True)
    
    def DoAction(self, action:BattleAction) -> bool:
        assert(action and not self.IsBattleOver())
        done = False
        if self.attacker_action:
            action.player_idx = self.armyA.hero.player_idx if self.armyA.hero else -1
        else:
            action.player_idx = self.armyD.hero.player_idx if self.armyD.hero else -1
        if action.target_pos:
            if self.attacker_action:
                target_stack:HOMMArmyStackInCombat = next((stack for stack in self.armyD if (stack.x, stack.y) == action.target_pos), None)
            else:
                target_stack:HOMMArmyStackInCombat = next((stack for stack in self.armyA if (stack.x, stack.y) == action.target_pos), None)
        else:
            target_stack=None
        if action.battle_action_type == 'spell':
            casterArmy:HOMMArmyInCombat = None
            action.result_what = HeroSpellUtils.GetSpellName(action.spell_id)
            has_mana = False
            if self.attacker_action:
                self.atk_round_spell = True
                casterArmy = self.armyA
                if not target_stack:
                    # because spells can be cast on own army stacks (buffs)
                    target_stack:HOMMArmyStackInCombat = next((stack for stack in self.armyA if (stack.x, stack.y) == action.target_pos), None)
            else:
                self.def_round_spell = True
                casterArmy = self.armyD
                if not target_stack:
                    # because spells can be cast on own army stacks (buffs)
                    target_stack:HOMMArmyStackInCombat = next((stack for stack in self.armyD if (stack.x, stack.y) == action.target_pos), None)
            assert(casterArmy)
            action.result_where = f'{target_stack.stack.GetUnitName()} at {(target_stack.x, target_stack.y)}'
            
            if casterArmy.curr_mana >= casterArmy.hero.GetSpellCost(action.spell_id):
                casterArmy.curr_mana -= casterArmy.hero.GetSpellCost(action.spell_id)
                if HeroSpellUtils.IsSpellDamage(action.spell_id):
                    damage = casterArmy.hero.GetSpellValue(action.spell_id)
                    damage *= (1 - casterArmy.hero.GetSkillValue(HeroSkillUtils.GetSkillId('Resistance')))
                    target_stack.TakeDamage(damage)
                    action.result_what += f' {damage} damage'
                else:
                    assert(HeroSpellUtils.IsSpellBuff(action.spell_id) or HeroSpellUtils.IsSpellCurse(action.spell_id))
                    target_stack.active_spells[action.spell_id] = casterArmy.hero.power if action.spell_id not in [HeroSpellUtils.GetSpellId('Frenzy')] else 1
                    # here we refresh stack order because the spell cast could change unit speed
                    self.RefreshStackOrder()
                # we do NOT updat current stack on spell cat
                done = True
        else:
            # TODO: implement actions 'wait' and 'defend' for army stacks in combat
            if target_stack:
                action.result_where = f'{target_stack.stack.GetUnitName()} at {(target_stack.x, target_stack.y)}'
            if action.battle_action_type == 'shoot':
                damage = self.GetDamageArmy(self.curr_stack, target_stack)
                target_stack.TakeDamage(damage)
                action.result_what = f'{damage} damage'
                action.end_pos = action.start_pos = action.dest = (self.curr_stack.x, self.curr_stack.y)
            else:
                assert('move' in action.battle_action_type)
                action.start_pos = (self.curr_stack.x, self.curr_stack.y)

                if action.dest == (self.curr_stack.x, self.curr_stack.y):
                    action.end_pos = action.dest
                else:
                    otherHero = self.armyD.hero if self.attacker_action else self.armyA.hero
                    path = self.battlefield.StackPathTo(self.curr_stack, action.dest)
                    dist = self.curr_stack.GetUnitSpeed(otherHero)
                    obstacles = self.battlefield.__get_obstacles__()
                    if UnitUtils.IsFlying(self.curr_stack.stack.unit_type):
                        idx = min(dist, len(path))-1
                        pos = path[idx]
                        if pos in obstacles:
                            self.prev_stack = self.curr_stack
                            return False
                    else:
                        for idx in range(min(dist, len(path))):
                            if path[idx] in obstacles:
                                idx -= 1
                                break
                    action.end_pos = path[idx]
                    self.curr_stack.x = action.end_pos[0]
                    self.curr_stack.y = action.end_pos[1]

                if 'attack' in action.battle_action_type:
                    damage = self.GetDamageArmy(self.curr_stack, target_stack)
                    target_stack.TakeDamage(damage)
                    action.result_what = f'{damage} damage'
                    if not target_stack.retaliated:
                        target_stack.retaliated = True
                        retal_damage = self.GetDamageArmy(target_stack, self.curr_stack)
                        self.curr_stack.TakeDamage(retal_damage)
                        action.result_what += f', {retal_damage} damage retaliated'
                else:
                    action.result_where = f'at {action.end_pos}'
            self.curr_stack.prev_round = self.curr_round
            self.prev_stack = self.curr_stack
            self.UpdateCurrentStack()
            done = True
        # invalid action
        return done

    def UpdateCurrentStack(self):
        next_attacking_stack:HOMMArmyStackInCombat = next((stack for stack in self.armyA if stack.prev_round < self.curr_round and stack.curr_num), None)
        next_defending_stack:HOMMArmyStackInCombat = next((stack for stack in self.armyD if stack.prev_round < self.curr_round and stack.curr_num), None)
        if next_attacking_stack:
            if next_defending_stack:
                if next_defending_stack.GetUnitSpeed(self.armyA.hero) > next_attacking_stack.GetUnitSpeed(self.armyD.hero):
                    # defending army has faster stack
                    self.curr_stack = next_defending_stack
                    self.attacker_action = False
            # attacking army has faster stack, or all defender stacks acted this round
            self.curr_stack = next_attacking_stack
            self.attacker_action = True
        else:
            # all attacking army stacks acted this round
            self.curr_stack = next_defending_stack
            self.attacker_action = False

    def NewRound(self):
        self.atk_round_spell = False
        self.def_round_spell = False
        self.curr_round += 1

        # decrease duration for all active spells
        for stack in self.armyA:
            stack.active_spells = [x-1 if x>0 else 0 for x in stack.active_spells]
            stack.retaliated = False
        for stack in self.armyD:
            stack.active_spells = [x-1 if x>0 else 0 for x in stack.active_spells]
            stack.retaliated = False
        
        # because spells may have expired we need to refresh stack order every round
        self.RefreshStackOrder()
        self.UpdateCurrentStack()

    def IsBattleOver(self) -> bool:
        return self.curr_round >= self.max_rounds or self.armyA.IsDefeated() or self.armyD.IsDefeated()
    
    def GetDamageArmy(self, currentStack:HOMMArmyStackInCombat, otherStack:HOMMArmyStackInCombat) -> int:
        """Tries to follow the rules from here: https://heroes.thelazy.net/index.php/Damage"""

        assert(currentStack and otherStack)
        curr_atk = currentStack.stack.GetAttack()
        other_def = otherStack.stack.GetDefense()
        if currentStack.hero:
            curr_atk += currentStack.hero.attack + currentStack.hero.GetBonus('attack')
        if otherStack.hero:
            other_def += otherStack.hero.defense + otherStack.hero.GetBonus('defense')
        
        # perhaps this code could be moved somewhere else?
        dmg_min, dmg_max = currentStack.stack.GetDamage()
        bless_id = HeroSpellUtils.GetSpellId('bless')
        curse_id = HeroSpellUtils.GetSpellId('curse')
        if currentStack.active_spells[bless_id] > 0:
            assert(currentStack.active_spells[curse_id] == 0)
            if currentStack.hero:
                dmg_max += currentStack.hero.GetSpellValue(bless_id)
            dmg_min = dmg_max
        elif currentStack.active_spells[curse_id] > 0:
            if otherStack.hero:
                dmg_min += otherStack.hero.GetSpellValue(curse_id)
            dmg_max = dmg_min
        
        if dmg_min < dmg_max:
            # TODO: this should be replaced with a random values provider, in order to replay exactly
            damage = currentStack.curr_num * self.rng.randint(dmg_min, dmg_max)
        else:
            damage = currentStack.curr_num * dmg_min

        I1 = min(0.05 * (curr_atk - other_def) if curr_atk > other_def else 0, 3.0)
        R1 = min(0.025 * (other_def - curr_atk) if other_def > curr_atk else 0, 0.7)

        I2 = 0
        is_ranged_attack = UnitUtils.IsRanged(currentStack.stack.unit_type)
        if currentStack.hero:
            if is_ranged_attack:
                I2 = currentStack.hero.GetSkillValue(HeroSkillUtils.GetSkillId('archery'))
            else:
                I2 = currentStack.hero.GetSkillValue(HeroSkillUtils.GetSkillId('offense'))

        # I3: modifier based on attacker hero specialty -- not supported yet
        I3 = 0

        # I4: modifier based on Luck -- not supported yet
        I4 = 0

        # I5: modifier based on unit type special ability -- not supported yet
        I5 = 0

        # modifier based on defender hero secondary stills
        R2 = 0
        if otherStack.hero:
            R2 = otherStack.hero.GetSkillValue(HeroSkillUtils.GetSkillId('armorer'))
        
        # R3: modifier based on defender hero specialty -- not supported yet
        R3 = 0

        # R4: modifier based on defensive buffs on defending army
        R4 = 0
        if otherStack.hero:
            if is_ranged_attack:
                air_shield_id = HeroSpellUtils.GetSpellId('air shield')
                if otherStack.active_spells[air_shield_id] > 0:
                    R4 = otherStack.hero.GetSpellValue(air_shield_id)
            else:
                shield_id = HeroSpellUtils.GetSpellId('shield')
                if otherStack.active_spells[shield_id] > 0:
                    R4 = otherStack.hero.GetSpellValue(shield_id)
        
        # R5:
        dist = self.battlefield.GetDistanceEvenR(currentStack.x, currentStack.y, otherStack.x, otherStack.y)
        R5 = 0
        if dist == 0 or dist > 10:
            R5 = 0.5
        
        # R6: modifier of obstacle, for ranged attacks -- not supported yet
        R6 = 0

        # R7: modifier for Blind and Forgetfullness -- not supported yet
        R7 = 0

        # R8: modifier for various other modifiers like phychic elemental vs mind immunity, petrified retaliation, paralized retaliation
        # -- not supported yet
        R8 = 0

        return int(damage * (1 + I1 + I2 + I3 + I4 + I5) * (1 - R1) * (1 - R2 - R3) * (1 - R4) * (1 - R5) * (1 - R6) * (1 - R7) * (1 - R8))

class BattleFactory(HOMMBattleFactory):
    def NewBattle(self, heroA:HOMMHero, armyD:HOMMArmy, layout:str) -> HOMMBattle:
        assert(heroA and armyD and layout and layout in HOMMBattle.BATTLE_LAYOUT)
        return Battle(heroA=heroA, armyD=armyD, layout=layout)
"""
Turn-based battle engine.

Turn order: sorted by Speed stat (ties broken randomly).
Each combatant acts once per round. Statuses tick at end of round.
"""
from __future__ import annotations
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Union

from stats import StatusEffect, Element, ELEMENT_WEAKNESSES
from skills import Skill, SkillType, TargetType, SKILLS
from character import Character
from enemy import Enemy
from items import ITEMS, Item

Combatant = Union[Character, Enemy]


class BattleResult(Enum):
    VICTORY = "victory"
    DEFEAT = "defeat"
    ESCAPED = "escaped"
    ONGOING = "ongoing"


@dataclass
class BattleAction:
    actor: Combatant
    action_type: str            # "skill" | "item" | "defend" | "run"
    skill: Skill | None = None
    item_id: str | None = None
    targets: list[Combatant] = field(default_factory=list)


def compute_damage(actor: Combatant, target: Combatant, skill: Skill) -> int:
    if skill.skill_type == SkillType.PHYSICAL:
        base = actor.stats.attack
        defense = target.stats.defense
    else:
        base = actor.stats.magic if isinstance(actor, Character) else actor.stats.magic
        defense = target.stats.magic_defense

    raw = int(base * skill.power / 100)
    raw = max(1, raw - defense // 2)

    # Elemental modifier
    multiplier = 1.0
    weaknesses = target.element_weaknesses if hasattr(target, "element_weaknesses") else []
    resistances = target.element_resistances if hasattr(target, "element_resistances") else []
    if skill.element in weaknesses:
        multiplier = 1.5
    elif skill.element in resistances:
        multiplier = 0.5

    # Defend status halves incoming damage
    if StatusEffect.DEFEND in target.status_effects:
        multiplier *= 0.5

    # ±10% random variance
    variance = random.uniform(0.9, 1.1)
    return max(1, int(raw * multiplier * variance))


def compute_heal(actor: Combatant, skill: Skill) -> int:
    magic = actor.stats.magic if isinstance(actor, Character) else 10
    base = int(magic * skill.power / 100)
    variance = random.uniform(0.9, 1.1)
    return max(1, int(base * variance))


class Battle:
    def __init__(self, party: list[Character], enemies: list[Enemy]) -> None:
        self.party = party
        self.enemies = enemies
        self.result = BattleResult.ONGOING
        self.round = 0
        self.log: list[str] = []

    def _log(self, msg: str) -> None:
        self.log.append(msg)

    @property
    def active_party(self) -> list[Character]:
        return [c for c in self.party if c.is_alive]

    @property
    def active_enemies(self) -> list[Enemy]:
        return [e for e in self.enemies if e.is_alive]

    def turn_order(self) -> list[Combatant]:
        combatants: list[Combatant] = self.active_party + self.active_enemies  # type: ignore[operator]
        return sorted(combatants, key=lambda c: (c.stats.speed + random.randint(0, 3)), reverse=True)

    def execute_action(self, action: BattleAction) -> list[str]:
        messages: list[str] = []
        actor = action.actor

        if action.action_type == "defend":
            actor.apply_status(StatusEffect.DEFEND)
            messages.append(f"{actor.name} takes a defensive stance!")
            return messages

        if action.action_type == "run":
            escape_chance = 60
            if random.randint(1, 100) <= escape_chance:
                self.result = BattleResult.ESCAPED
                messages.append("The party escaped!")
            else:
                messages.append("Couldn't escape!")
            return messages

        if action.action_type == "item":
            item_id = action.item_id
            item = ITEMS[item_id]  # type: ignore[index]
            for target in action.targets:
                msgs = self._apply_item(item, target)
                messages.extend(msgs)
            return messages

        # skill action
        skill = action.skill
        if skill is None:
            return messages

        if StatusEffect.SILENCE in actor.status_effects and skill.mp_cost > 0:
            messages.append(f"{actor.name} is Silenced and can't cast {skill.name}!")
            return messages

        if isinstance(actor, Character) and actor.mp < skill.mp_cost:
            messages.append(f"{actor.name} doesn't have enough MP!")
            return messages

        if isinstance(actor, Character):
            actor.mp -= skill.mp_cost

        if skill.skill_type in (SkillType.PHYSICAL, SkillType.MAGIC, SkillType.DEBUFF):
            for target in action.targets:
                msgs = self._apply_offensive_skill(actor, target, skill)
                messages.extend(msgs)
        elif skill.skill_type == SkillType.HEALING:
            for target in action.targets:
                msgs = self._apply_healing_skill(actor, target, skill)
                messages.extend(msgs)
        elif skill.skill_type == SkillType.BUFF:
            for target in action.targets:
                if skill.status_effect:
                    applied = target.apply_status(skill.status_effect)
                    if applied:
                        messages.append(f"{target.name} is now in a {skill.status_effect.value} state!")

        return messages

    def _apply_offensive_skill(self, actor: Combatant, target: Combatant, skill: Skill) -> list[str]:
        messages: list[str] = []
        dmg = compute_damage(actor, target, skill)
        actual = target.take_damage(dmg)

        elem_note = f" [{skill.element.value.upper()}]" if skill.element != Element.NONE else ""
        messages.append(f"{actor.name} uses {skill.name}{elem_note} on {target.name} for {actual} damage!")

        if not target.is_alive:
            messages.append(f"{target.name} was defeated!")
        elif skill.status_effect and skill.status_chance > 0:
            if random.randint(1, 100) <= skill.status_chance:
                applied = target.apply_status(skill.status_effect)
                if applied:
                    messages.append(f"{target.name} is afflicted with {skill.status_effect.value.upper()}!")

        return messages

    def _apply_healing_skill(self, actor: Combatant, target: Combatant, skill: Skill) -> list[str]:
        messages: list[str] = []
        if skill.name == "Esuna":
            target.clear_status()
            messages.append(f"{actor.name} casts Esuna on {target.name}. All status effects cleared!")
        else:
            amount = compute_heal(actor, skill)
            restored = target.restore_hp(amount)
            messages.append(f"{actor.name} casts {skill.name} on {target.name}. Restored {restored} HP!")
        return messages

    def _apply_item(self, item: Item, target: Combatant) -> list[str]:
        messages: list[str] = []
        if item.revive and isinstance(target, Character) and target.is_ko:
            target.hp = 1
            messages.append(f"Phoenix Down revives {target.name}!")
            return messages
        if item.clears_status:
            target.clear_status()
            messages.append(f"{item.name} clears {target.name}'s status effects!")
        if item.hp_restore and isinstance(target, Character):
            restored = target.restore_hp(item.hp_restore)
            messages.append(f"{item.name} restores {restored} HP to {target.name}!")
        if item.mp_restore and isinstance(target, Character):
            restored = target.restore_mp(item.mp_restore)
            messages.append(f"{item.name} restores {restored} MP to {target.name}!")
        return messages

    def tick_statuses(self) -> list[str]:
        """Called at the end of each round. DoT / regen effects."""
        messages: list[str] = []
        for combatant in self.active_party + self.active_enemies:  # type: ignore[operator]
            if StatusEffect.POISON in combatant.status_effects:
                dmg = max(1, combatant.stats.max_hp // 16)
                combatant.take_damage(dmg)
                messages.append(f"{combatant.name} takes {dmg} poison damage!")
                if not combatant.is_alive:
                    messages.append(f"{combatant.name} was defeated by poison!")
            if StatusEffect.BURN in combatant.status_effects:
                dmg = max(1, combatant.stats.max_hp // 12)
                combatant.take_damage(dmg)
                messages.append(f"{combatant.name} takes {dmg} burn damage!")
            if StatusEffect.REGEN in combatant.status_effects:
                heal = max(1, combatant.stats.max_hp // 12)
                if isinstance(combatant, Character):
                    combatant.restore_hp(heal)
                messages.append(f"{combatant.name} regenerates {heal} HP!")
            # Freeze / Stun: cleared after one round
            for expiring in (StatusEffect.FREEZE, StatusEffect.STUN, StatusEffect.DEFEND):
                combatant.clear_status(expiring)
        return messages

    def check_result(self) -> BattleResult:
        if not self.active_enemies:
            self.result = BattleResult.VICTORY
        elif not self.active_party:
            self.result = BattleResult.DEFEAT
        return self.result

    def collect_rewards(self) -> tuple[int, int, list[str]]:
        """Returns (total_exp, total_gold, dropped_item_ids)."""
        total_exp = sum(e.exp_reward for e in self.enemies)
        total_gold = sum(e.gold_reward for e in self.enemies)
        drops: list[str] = []
        for e in self.enemies:
            drops.extend(e.roll_drops())
        return total_exp, total_gold, drops

    def enemy_turn(self, enemy: Enemy) -> list[str]:
        """Auto-resolve an enemy's turn."""
        if StatusEffect.STUN in enemy.status_effects or StatusEffect.FREEZE in enemy.status_effects:
            return [f"{enemy.name} is immobilized and cannot act!"]

        skill = enemy.choose_action()
        targets: list[Combatant]

        if skill.target.name.startswith("ALL_ALLIES"):
            # allies = party from enemy's perspective
            targets = self.active_party  # type: ignore[assignment]
        else:
            targets = [random.choice(self.active_party)]  # type: ignore[assignment]

        action = BattleAction(actor=enemy, action_type="skill", skill=skill, targets=targets)
        return self.execute_action(action)

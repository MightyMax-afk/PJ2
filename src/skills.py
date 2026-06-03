from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from stats import Element, StatusEffect


class SkillType(Enum):
    PHYSICAL = "physical"
    MAGIC = "magic"
    HEALING = "healing"
    BUFF = "buff"
    DEBUFF = "debuff"


class TargetType(Enum):
    SINGLE_ENEMY = "single_enemy"
    ALL_ENEMIES = "all_enemies"
    SINGLE_ALLY = "single_ally"
    ALL_ALLIES = "all_allies"
    SELF = "self"


@dataclass
class Skill:
    name: str
    skill_type: SkillType
    target: TargetType
    mp_cost: int
    power: int                          # base damage/heal multiplier (%)
    element: Element = Element.NONE
    status_effect: Optional[StatusEffect] = None
    status_chance: int = 0              # % chance to apply status
    description: str = ""

    def __str__(self) -> str:
        cost = f"{self.mp_cost} MP" if self.mp_cost > 0 else "0 MP"
        return f"{self.name} ({cost}) — {self.description}"


# ── Shared skill library ───────────────────────────────────────────────────────
SKILLS: dict[str, Skill] = {
    # Physical
    "attack":       Skill("Attack",       SkillType.PHYSICAL, TargetType.SINGLE_ENEMY,  0, 100, description="A basic physical strike."),
    "power_strike":  Skill("Power Strike",  SkillType.PHYSICAL, TargetType.SINGLE_ENEMY,  6, 160, description="A heavy blow dealing extra damage."),
    "double_slash":  Skill("Double Slash",  SkillType.PHYSICAL, TargetType.ALL_ENEMIES,   8, 80,  description="Slash all enemies for moderate damage."),
    "cross_cut":     Skill("Cross Cut",     SkillType.PHYSICAL, TargetType.SINGLE_ENEMY, 10, 220, description="A brutal cross-shaped cut."),

    # Fire magic
    "fire":          Skill("Fire",          SkillType.MAGIC, TargetType.SINGLE_ENEMY,  4, 120, Element.FIRE,      description="Small burst of flame."),
    "fira":          Skill("Fira",          SkillType.MAGIC, TargetType.SINGLE_ENEMY,  8, 200, Element.FIRE,      description="Medium burst of flame."),
    "firaga":        Skill("Firaga",        SkillType.MAGIC, TargetType.ALL_ENEMIES,  14, 180, Element.FIRE,      description="Firestorm hits all enemies."),

    # Ice magic
    "blizzard":      Skill("Blizzard",      SkillType.MAGIC, TargetType.SINGLE_ENEMY,  4, 120, Element.ICE, StatusEffect.FREEZE, 15, "Icy blast, chance to Freeze."),
    "blizzara":      Skill("Blizzara",      SkillType.MAGIC, TargetType.SINGLE_ENEMY,  8, 200, Element.ICE, StatusEffect.FREEZE, 20, "Stronger icy blast."),

    # Lightning magic
    "thunder":       Skill("Thunder",       SkillType.MAGIC, TargetType.SINGLE_ENEMY,  4, 120, Element.LIGHTNING,  description="Bolt of lightning."),
    "thundara":      Skill("Thundara",      SkillType.MAGIC, TargetType.ALL_ENEMIES,   10, 150, Element.LIGHTNING,  description="Lightning hits all enemies."),

    # Healing
    "cure":          Skill("Cure",          SkillType.HEALING, TargetType.SINGLE_ALLY,   4, 80,  description="Restores a small amount of HP."),
    "cura":          Skill("Cura",          SkillType.HEALING, TargetType.SINGLE_ALLY,   8, 150, description="Restores a moderate amount of HP."),
    "curaga":        Skill("Curaga",        SkillType.HEALING, TargetType.ALL_ALLIES,   14, 120, description="Heals all allies for moderate HP."),
    "esuna":         Skill("Esuna",         SkillType.HEALING, TargetType.SINGLE_ALLY,   6,   0, description="Removes all status ailments."),

    # Buff / Debuff
    "protect":       Skill("Protect",       SkillType.BUFF,   TargetType.SINGLE_ALLY,   6,   0, status_effect=StatusEffect.DEFEND, status_chance=100, description="Raises DEF for one battle."),
    "poison_bite":   Skill("Poison Bite",   SkillType.PHYSICAL, TargetType.SINGLE_ENEMY, 4, 80, status_effect=StatusEffect.POISON, status_chance=40, description="Attack that may Poison the target."),
    "silence_arrow": Skill("Silence Arrow", SkillType.PHYSICAL, TargetType.SINGLE_ENEMY, 4, 60, status_effect=StatusEffect.SILENCE, status_chance=60, description="Arrow that may Silence the target."),

    # Dark / special
    "darkness":      Skill("Darkness",      SkillType.MAGIC, TargetType.ALL_ENEMIES,  12, 170, Element.DARK,  description="Dark energy damages all foes."),
    "holy":          Skill("Holy",          SkillType.MAGIC, TargetType.SINGLE_ENEMY, 16, 300, Element.LIGHT, description="Brilliant light obliterates one foe."),
}

from dataclasses import dataclass, field
from typing import Optional
import random
from stats import Stats, StatusEffect, Element
from skills import Skill, SKILLS


@dataclass
class EnemyAction:
    skill_id: str
    weight: int = 100       # relative chance weight


@dataclass
class Enemy:
    name: str
    stats: Stats
    actions: list[EnemyAction]
    exp_reward: int
    gold_reward: int
    element_weaknesses: list[Element] = field(default_factory=list)
    element_resistances: list[Element] = field(default_factory=list)
    drop_items: list[tuple[str, int]] = field(default_factory=list)  # (item_id, % chance)

    # Runtime state
    hp: int = field(default=0, init=False)
    mp: int = field(default=0, init=False)
    status_effects: set[StatusEffect] = field(default_factory=set, init=False)

    def __post_init__(self) -> None:
        self.hp = self.stats.max_hp
        self.mp = self.stats.max_mp

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def choose_action(self) -> Skill:
        total = sum(a.weight for a in self.actions)
        roll = random.randint(1, total)
        cumulative = 0
        for action in self.actions:
            cumulative += action.weight
            if roll <= cumulative:
                return SKILLS[action.skill_id]
        return SKILLS[self.actions[-1].skill_id]

    def take_damage(self, amount: int) -> int:
        actual = max(1, amount)
        self.hp = max(0, self.hp - actual)
        return actual

    def apply_status(self, effect: StatusEffect) -> bool:
        if effect in self.status_effects:
            return False
        self.status_effects.add(effect)
        return True

    def clear_status(self, effect: StatusEffect | None = None) -> None:
        if effect is None:
            self.status_effects.clear()
        else:
            self.status_effects.discard(effect)

    def hp_bar(self, width: int = 20) -> str:
        ratio = self.hp / self.stats.max_hp
        filled = round(ratio * width)
        return f"[{'#' * filled}{'.' * (width - filled)}]"

    def status_str(self) -> str:
        if not self.status_effects:
            return ""
        return " [" + ",".join(e.value.upper()[:3] for e in self.status_effects) + "]"

    def roll_drops(self) -> list[str]:
        drops: list[str] = []
        for item_id, chance in self.drop_items:
            if random.randint(1, 100) <= chance:
                drops.append(item_id)
        return drops

    def __str__(self) -> str:
        return f"{self.name} HP:{self.hp}/{self.stats.max_hp}{self.status_str()}"


# ── Enemy factory ─────────────────────────────────────────────────────────────

def make_slime() -> Enemy:
    return Enemy(
        name="Slime",
        stats=Stats(max_hp=60, max_mp=0, attack=8, defense=4, magic=0, magic_defense=4, speed=8),
        actions=[EnemyAction("attack", 100)],
        exp_reward=20, gold_reward=10,
        drop_items=[("potion", 30)],
    )


def make_goblin() -> Enemy:
    return Enemy(
        name="Goblin",
        stats=Stats(max_hp=90, max_mp=0, attack=14, defense=8, magic=0, magic_defense=5, speed=12),
        actions=[EnemyAction("attack", 70), EnemyAction("power_strike", 30)],
        exp_reward=35, gold_reward=18,
        drop_items=[("potion", 20), ("antidote", 10)],
    )


def make_fire_sprite() -> Enemy:
    return Enemy(
        name="Fire Sprite",
        stats=Stats(max_hp=75, max_mp=40, attack=10, defense=6, magic=18, magic_defense=12, speed=16),
        actions=[EnemyAction("attack", 40), EnemyAction("fire", 60)],
        exp_reward=45, gold_reward=22,
        element_weaknesses=[Element.ICE],
        element_resistances=[Element.FIRE],
        drop_items=[("ether", 25)],
    )


def make_wolf_pack() -> Enemy:
    return Enemy(
        name="Wolf Pack",
        stats=Stats(max_hp=140, max_mp=0, attack=20, defense=10, magic=0, magic_defense=8, speed=18),
        actions=[EnemyAction("attack", 50), EnemyAction("double_slash", 50)],
        exp_reward=55, gold_reward=30,
        drop_items=[("potion", 15)],
    )


def make_dark_knight() -> Enemy:
    return Enemy(
        name="Dark Knight",
        stats=Stats(max_hp=280, max_mp=60, attack=30, defense=20, magic=14, magic_defense=14, speed=10),
        actions=[EnemyAction("attack", 40), EnemyAction("power_strike", 35), EnemyAction("darkness", 25)],
        exp_reward=120, gold_reward=80,
        element_weaknesses=[Element.LIGHT],
        element_resistances=[Element.DARK],
        drop_items=[("hi_potion", 40), ("ether", 20)],
    )


def make_dragon_boss() -> Enemy:
    return Enemy(
        name="Ancient Dragon",
        stats=Stats(max_hp=1200, max_mp=120, attack=45, defense=30, magic=35, magic_defense=25, speed=14),
        actions=[
            EnemyAction("attack",      30),
            EnemyAction("power_strike", 25),
            EnemyAction("firaga",       25),
            EnemyAction("double_slash", 20),
        ],
        exp_reward=500, gold_reward=300,
        element_weaknesses=[Element.ICE],
        element_resistances=[Element.FIRE],
        drop_items=[("elixir", 50), ("hi_ether", 60), ("phoenix_down", 30)],
    )


ENCOUNTER_POOLS: dict[str, list] = {
    "forest":   [make_slime, make_goblin, make_wolf_pack],
    "cave":     [make_goblin, make_fire_sprite, make_dark_knight],
    "dungeon":  [make_dark_knight, make_dragon_boss],
}


def random_encounter(zone: str) -> list[Enemy]:
    import random
    pool = ENCOUNTER_POOLS.get(zone, [make_slime])
    count = random.randint(1, min(3, len(pool)))
    return [random.choice(pool)() for _ in range(count)]

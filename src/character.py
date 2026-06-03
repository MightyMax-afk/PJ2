from dataclasses import dataclass, field
from typing import Optional
from stats import Stats, StatusEffect, Element
from skills import Skill, SKILLS


LEVEL_EXP_TABLE = [0, 100, 250, 450, 700, 1000, 1400, 1900, 2500, 3200, 4000,
                   5000, 6200, 7600, 9200, 11000, 13000, 15200, 17600, 20200, 23000]


@dataclass
class Character:
    name: str
    base_stats: Stats
    skill_list: list[str]               # skill IDs learned at character creation
    level_up_skills: dict[int, str]     # {level: skill_id} learned on level up
    element_weaknesses: list[Element] = field(default_factory=list)
    element_resistances: list[Element] = field(default_factory=list)

    # Runtime state (not base data)
    level: int = field(default=1, init=False)
    exp: int = field(default=0, init=False)
    hp: int = field(default=0, init=False)
    mp: int = field(default=0, init=False)
    status_effects: set[StatusEffect] = field(default_factory=set, init=False)
    _stats: Optional[Stats] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self._stats = self.base_stats.copy()
        self.hp = self._stats.max_hp
        self.mp = self._stats.max_mp

    @property
    def stats(self) -> Stats:
        return self._stats  # type: ignore[return-value]

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    @property
    def is_ko(self) -> bool:
        return self.hp <= 0

    @property
    def exp_to_next(self) -> int:
        if self.level >= len(LEVEL_EXP_TABLE) - 1:
            return 0
        return LEVEL_EXP_TABLE[self.level] - self.exp

    def gain_exp(self, amount: int) -> list[str]:
        """Returns list of messages (level ups, skills learned)."""
        messages: list[str] = []
        self.exp += amount
        while (self.level < len(LEVEL_EXP_TABLE) - 1
               and self.exp >= LEVEL_EXP_TABLE[self.level]):
            self.level += 1
            self._level_up_stats()
            messages.append(f"{self.name} reached Level {self.level}!")
            if self.level in self.level_up_skills:
                skill_id = self.level_up_skills[self.level]
                self.skill_list.append(skill_id)
                messages.append(f"{self.name} learned {SKILLS[skill_id].name}!")
        return messages

    def _level_up_stats(self) -> None:
        s = self._stats
        s.max_hp += 20
        s.max_mp += 5
        s.attack += 2
        s.defense += 1
        s.magic += 2
        s.magic_defense += 1
        s.speed += 1
        self.hp = min(self.hp + 20, s.max_hp)
        self.mp = min(self.mp + 5, s.max_mp)

    def apply_status(self, effect: StatusEffect) -> bool:
        """Returns True if the effect was newly applied."""
        if effect in self.status_effects:
            return False
        self.status_effects.add(effect)
        return True

    def clear_status(self, effect: StatusEffect | None = None) -> None:
        if effect is None:
            self.status_effects.clear()
        else:
            self.status_effects.discard(effect)

    def take_damage(self, amount: int) -> int:
        actual = max(1, amount)
        self.hp = max(0, self.hp - actual)
        return actual

    def restore_hp(self, amount: int) -> int:
        before = self.hp
        self.hp = min(self.stats.max_hp, self.hp + amount)
        return self.hp - before

    def restore_mp(self, amount: int) -> int:
        before = self.mp
        self.mp = min(self.stats.max_mp, self.mp + amount)
        return self.mp - before

    def hp_bar(self, width: int = 20) -> str:
        ratio = self.hp / self.stats.max_hp
        filled = round(ratio * width)
        return f"[{'#' * filled}{'.' * (width - filled)}]"

    def status_str(self) -> str:
        if not self.status_effects:
            return ""
        return " [" + ",".join(e.value.upper()[:3] for e in self.status_effects) + "]"

    def __str__(self) -> str:
        return (f"{self.name} Lv{self.level} "
                f"HP:{self.hp}/{self.stats.max_hp} "
                f"MP:{self.mp}/{self.stats.max_mp}"
                f"{self.status_str()}")


# ── Predefined playable character templates ───────────────────────────────────

def make_warrior(name: str = "Kael") -> Character:
    return Character(
        name=name,
        base_stats=Stats(max_hp=320, max_mp=40, attack=28, defense=22,
                         magic=8, magic_defense=10, speed=12),
        skill_list=["attack", "power_strike"],
        level_up_skills={4: "double_slash", 8: "cross_cut", 14: "protect"},
    )


def make_mage(name: str = "Lyra") -> Character:
    return Character(
        name=name,
        base_stats=Stats(max_hp=180, max_mp=140, attack=10, defense=8,
                         magic=30, magic_defense=20, speed=14),
        skill_list=["attack", "fire", "blizzard", "thunder"],
        level_up_skills={3: "cure", 5: "fira", 7: "thundara",
                         10: "blizzara", 15: "firaga", 18: "holy"},
    )


def make_rogue(name: str = "Shen") -> Character:
    return Character(
        name=name,
        base_stats=Stats(max_hp=220, max_mp=60, attack=22, defense=14,
                         magic=12, magic_defense=12, speed=22),
        skill_list=["attack", "poison_bite", "silence_arrow"],
        level_up_skills={5: "double_slash", 9: "cross_cut", 12: "darkness"},
    )


def make_healer(name: str = "Aria") -> Character:
    return Character(
        name=name,
        base_stats=Stats(max_hp=240, max_mp=160, attack=12, defense=14,
                         magic=24, magic_defense=22, speed=16),
        skill_list=["attack", "cure", "esuna"],
        level_up_skills={3: "protect", 6: "cura", 11: "curaga",
                         16: "holy"},
    )

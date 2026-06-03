from dataclasses import dataclass, field
from enum import Enum


class Element(Enum):
    NONE = "none"
    FIRE = "fire"
    ICE = "ice"
    LIGHTNING = "lightning"
    WIND = "wind"
    EARTH = "earth"
    LIGHT = "light"
    DARK = "dark"


class StatusEffect(Enum):
    POISON = "poison"
    BURN = "burn"
    FREEZE = "freeze"
    STUN = "stun"
    BLIND = "blind"
    SILENCE = "silence"
    REGEN = "regen"
    DEFEND = "defend"


@dataclass
class Stats:
    max_hp: int
    max_mp: int
    attack: int
    defense: int
    magic: int
    magic_defense: int
    speed: int
    luck: int = 5

    def copy(self) -> "Stats":
        return Stats(
            self.max_hp, self.max_mp, self.attack, self.defense,
            self.magic, self.magic_defense, self.speed, self.luck
        )


ELEMENT_WEAKNESSES: dict[Element, Element] = {
    Element.FIRE:      Element.ICE,
    Element.ICE:       Element.FIRE,
    Element.LIGHTNING: Element.EARTH,
    Element.EARTH:     Element.LIGHTNING,
    Element.WIND:      Element.LIGHTNING,
    Element.LIGHT:     Element.DARK,
    Element.DARK:      Element.LIGHT,
}

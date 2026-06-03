from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from stats import StatusEffect


class ItemType(Enum):
    CONSUMABLE = "consumable"
    KEY = "key"


@dataclass
class Item:
    name: str
    item_type: ItemType
    description: str
    hp_restore: int = 0
    mp_restore: int = 0
    revive: bool = False                # revives KO'd ally to 1 HP
    clears_status: bool = False
    value: int = 0                      # buy price in gold

    def __str__(self) -> str:
        return f"{self.name} — {self.description}"


@dataclass
class Inventory:
    items: dict[str, int] = field(default_factory=dict)  # item_id -> quantity

    def add(self, item_id: str, qty: int = 1) -> None:
        self.items[item_id] = self.items.get(item_id, 0) + qty

    def remove(self, item_id: str, qty: int = 1) -> bool:
        if self.items.get(item_id, 0) < qty:
            return False
        self.items[item_id] -= qty
        if self.items[item_id] == 0:
            del self.items[item_id]
        return True

    def has(self, item_id: str) -> bool:
        return self.items.get(item_id, 0) > 0

    def count(self, item_id: str) -> int:
        return self.items.get(item_id, 0)


ITEMS: dict[str, Item] = {
    "potion":      Item("Potion",      ItemType.CONSUMABLE, "Restores 100 HP.",          hp_restore=100,  value=50),
    "hi_potion":   Item("Hi-Potion",   ItemType.CONSUMABLE, "Restores 300 HP.",          hp_restore=300,  value=150),
    "mega_potion": Item("Mega-Potion", ItemType.CONSUMABLE, "Restores 1000 HP.",         hp_restore=1000, value=500),
    "ether":       Item("Ether",       ItemType.CONSUMABLE, "Restores 50 MP.",           mp_restore=50,   value=80),
    "hi_ether":    Item("Hi-Ether",    ItemType.CONSUMABLE, "Restores 150 MP.",          mp_restore=150,  value=250),
    "elixir":      Item("Elixir",      ItemType.CONSUMABLE, "Fully restores HP and MP.", hp_restore=9999, mp_restore=9999, value=2000),
    "antidote":    Item("Antidote",    ItemType.CONSUMABLE, "Cures Poison and Burn.",    clears_status=True, value=30),
    "echo_screen": Item("Echo Screen", ItemType.CONSUMABLE, "Cures Silence.",            clears_status=True, value=30),
    "soft":        Item("Soft",        ItemType.CONSUMABLE, "Cures Freeze.",             clears_status=True, value=30),
    "phoenix_down":Item("Phoenix Down",ItemType.CONSUMABLE, "Revives a KO'd ally.",      revive=True, value=300),
}
